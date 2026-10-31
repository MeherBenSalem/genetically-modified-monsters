"""Sound synthesis toolkit for Spore & Stem (pure numpy + ffmpeg/libvorbis).

Everything is deterministic (seeded). Filters work in the frequency domain with smooth gain curves, so they are fast
and never ring harshly. Building blocks:

- oscillators driven by a frequency curve (phase-integrated, so sweeps are glitch-free): sine, soft saw, pulse
- noise (white, pink) and granular textures (crackle, dirt, clicks)
- envelopes from breakpoints, exponential decays, tremolo/flutter
- spectral filters (low/high/band pass, formant vowels) and a small room reverb
- loudness normalisation to a target RMS with a peak ceiling, short fades, OGG Vorbis encoding
"""
from __future__ import annotations

import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

RATE = 44100


class Rng:
    def __init__(self, seed: int):
        self.g = np.random.default_rng(seed)

    def uniform(self, a=0.0, b=1.0, size=None):
        return self.g.uniform(a, b, size)

    def normal(self, size):
        return self.g.normal(0.0, 1.0, size)

    def choice(self, items):
        return items[int(self.g.integers(0, len(items)))]


def n_of(seconds: float) -> int:
    return max(1, int(round(seconds * RATE)))


def time(seconds: float) -> np.ndarray:
    return np.arange(n_of(seconds)) / RATE


# ---------------------------------------------------------------------------------------------- envelopes and curves

def curve(seconds: float, *points, shape: str = "linear") -> np.ndarray:
    """Breakpoints (t, value) across the duration. shape 'exp' interpolates in log space (for frequencies)."""
    t = time(seconds)
    ts = np.array([p[0] for p in points], float)
    vs = np.array([p[1] for p in points], float)
    if shape == "exp":
        return np.exp(np.interp(t, ts, np.log(np.maximum(vs, 1e-6))))
    return np.interp(t, ts, vs)


def smooth_env(seconds: float, attack: float, release: float, hold_level: float = 1.0) -> np.ndarray:
    """A raised-cosine attack and release around a flat hold."""
    n = n_of(seconds)
    e = np.full(n, hold_level)
    a, r = min(n, n_of(attack)), min(n, n_of(release))
    if a > 0:
        e[:a] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    if r > 0:
        e[n - r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return e


def decay(seconds: float, tau: float, attack: float = 0.004) -> np.ndarray:
    t = time(seconds)
    e = np.exp(-t / tau)
    a = n_of(attack)
    e[:a] *= np.linspace(0, 1, a)
    return e


def tremolo(seconds: float, rate: float, depth: float, rng: Rng | None = None) -> np.ndarray:
    t = time(seconds)
    phase = rng.uniform(0, 6.28) if rng else 0.0
    return 1.0 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t + phase))


# ---------------------------------------------------------------------------------------------- sources

def osc(freq, shape: str = "sine", phase: float = 0.0) -> np.ndarray:
    """freq: an array (Hz per sample). shapes: sine, saw (band-limited soft), tri, pulse."""
    ph = 2 * np.pi * np.cumsum(freq) / RATE + phase
    if shape == "sine":
        return np.sin(ph)
    if shape == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if shape == "saw":
        # Sum a few harmonics with gentle rolloff; harmonics above ~9 kHz are left out to stay soft.
        out = np.zeros_like(ph)
        for k in range(1, 18):
            mask = (freq * k) < 9000
            out += mask * np.sin(k * ph) / k ** 1.15
        return out * 0.6
    if shape == "pulse":
        out = np.zeros_like(ph)
        for k in range(1, 18, 2):
            mask = (freq * k) < 9000
            out += mask * np.sin(k * ph) / k
        return out * 0.9
    raise ValueError(shape)


def noise(seconds: float, rng: Rng, color: str = "white") -> np.ndarray:
    x = rng.normal(n_of(seconds))
    if color == "pink":
        x = spectral(x, lambda f: 1 / np.sqrt(np.maximum(f, 20) / 20))
    elif color == "brown":
        x = spectral(x, lambda f: 1 / (np.maximum(f, 20) / 20))
    return x / (np.std(x) + 1e-9)


def grains(seconds: float, rng: Rng, density: float, grain: float = 0.004, lo: float = 800, hi: float = 6000,
           envelope: np.ndarray | None = None, jitter: float = 1.0) -> np.ndarray:
    """Short noisy ticks scattered in time (crackle, dirt, clicks). density: grains per second."""
    n = n_of(seconds)
    out = np.zeros(n)
    count = max(1, int(density * seconds))
    times = np.sort(rng.uniform(0, seconds, count))
    g = n_of(grain)
    win = np.hanning(max(4, g))
    for t0 in times:
        i = int(t0 * RATE)
        if envelope is not None and rng.uniform() > envelope[min(i, n - 1)] * jitter + (1 - jitter):
            continue
        seg = rng.normal(len(win)) * win * rng.uniform(0.3, 1.0)
        j = min(n, i + len(win))
        out[i:j] += seg[: j - i]
    return bandpass(out, lo, hi)


# ---------------------------------------------------------------------------------------------- filters

def spectral(x: np.ndarray, gain) -> np.ndarray:
    """Applies a zero-phase frequency-domain gain curve gain(freqs) -> gains."""
    n = len(x)
    size = 1 << int(np.ceil(np.log2(max(2, n * 2))))
    spec = np.fft.rfft(x, size)
    freqs = np.fft.rfftfreq(size, 1 / RATE)
    y = np.fft.irfft(spec * gain(freqs), size)[:n]
    return y


def lowpass(x, cutoff: float, slope: float = 4.0):
    return spectral(x, lambda f: 1 / (1 + (f / cutoff) ** slope))


def highpass(x, cutoff: float, slope: float = 4.0):
    return spectral(x, lambda f: 1 / (1 + (cutoff / np.maximum(f, 1e-3)) ** slope))


def bandpass(x, lo: float, hi: float, slope: float = 4.0):
    return highpass(lowpass(x, hi, slope), lo, slope)


def peak(x, centre: float, width_oct: float = 0.5, gain: float = 1.0):
    """A bell around centre (width in octaves)."""
    def g(f):
        d = np.log2(np.maximum(f, 1.0) / centre) / width_oct
        return 1 + gain * np.exp(-0.5 * d * d)
    return spectral(x, g)


VOWELS = {  # formant centres (Hz) and relative gains
    "a": ((750, 1.0), (1150, 0.6), (2600, 0.25)),
    "o": ((450, 1.0), (800, 0.5), (2600, 0.12)),
    "u": ((320, 1.0), (750, 0.35), (2300, 0.08)),
    "e": ((450, 1.0), (1800, 0.55), (2600, 0.3)),
    "i": ((300, 1.0), (2300, 0.6), (3100, 0.35)),
    "uh": ((550, 1.0), (1000, 0.5), (2500, 0.15)),
}


def formant(x, vowel: str, shift: float = 1.0, width_oct: float = 0.35):
    """Filters a buzzy source through vowel formants (shift scales them: >1 small creature, <1 big)."""
    bands = VOWELS[vowel]

    def g(f):
        total = np.zeros_like(f) + 0.02
        for centre, amp in bands:
            d = np.log2(np.maximum(f, 1.0) / (centre * shift)) / width_oct
            total += amp * np.exp(-0.5 * d * d)
        return total
    return spectral(x, g)


def reverb(x, seconds: float = 0.6, mix: float = 0.18, seed: int = 7, damp: float = 3500.0):
    """A small soft room: convolution with decaying, darkened noise."""
    rng = Rng(seed)
    ir = rng.normal(n_of(seconds)) * np.exp(-time(seconds) / (seconds / 5))
    ir = lowpass(ir, damp)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    n = len(x) + len(ir)
    size = 1 << int(np.ceil(np.log2(n)))
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x) + len(ir) // 2]
    dry = np.concatenate([x, np.zeros(len(wet) - len(x))])
    return dry * (1 - mix) + wet * mix * 3.0


# ---------------------------------------------------------------------------------------------- composition

def pad(x, seconds: float) -> np.ndarray:
    n = n_of(seconds)
    return np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n] if len(x) < n else x


def place(dest: np.ndarray, x: np.ndarray, at: float, gain: float = 1.0) -> np.ndarray:
    i = n_of(at) if at > 0 else 0
    j = min(len(dest), i + len(x))
    if j > i:
        dest[i:j] += x[: j - i] * gain
    return dest


def mixdown(seconds: float, *layers) -> np.ndarray:
    """layers: (signal, start_seconds, gain)."""
    out = np.zeros(n_of(seconds))
    for sig, at, gain in layers:
        place(out, sig, at, gain)
    return out


def finish(x: np.ndarray, rms_db: float = -18.0, ceiling_db: float = -1.0, fade: float = 0.006) -> np.ndarray:
    """Removes DC, fades the edges, normalises loudness to rms_db and limits the peak to ceiling_db."""
    x = x - np.mean(x)
    x = highpass(x, 35.0, 2.0)
    # Trim trailing near-silence, then fade both edges (fading last, so a trim never leaves a click).
    level = np.abs(x)
    idx = np.nonzero(level > 10 ** (-60 / 20) * (level.max() + 1e-12))[0]
    if len(idx):
        x = x[: min(len(x), idx[-1] + n_of(0.02))].copy()
    f = min(len(x) // 2, n_of(fade))
    tail = min(len(x) // 2, n_of(max(fade, 0.03)))
    if f > 0:
        x[:f] *= np.linspace(0, 1, f)
    if tail > 0:
        x[-tail:] *= np.linspace(1, 0, tail) ** 2
    # Loudness over the loud part only, so long tails don't inflate the gain.
    active = x[np.abs(x) > 0.05 * (np.abs(x).max() + 1e-12)]
    rms = np.sqrt(np.mean(active ** 2)) if len(active) else 1e-9
    x = x * (10 ** (rms_db / 20) / (rms + 1e-12))
    pk = np.abs(x).max()
    ceil = 10 ** (ceiling_db / 20)
    if pk > ceil:
        # Soft-knee limiting: tanh above 70% of the ceiling.
        knee = 0.7 * ceil
        over = np.abs(x) > knee
        x[over] = np.sign(x[over]) * (knee + (ceil - knee) * np.tanh((np.abs(x[over]) - knee) / (ceil - knee)))
    return x.astype(np.float32)


def encode_ogg(x: np.ndarray, path: Path, quality: int = 4) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "x.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(pcm.tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-c:a", "libvorbis",
                        "-q:a", str(quality), "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact",
                        str(path)], check=True)
