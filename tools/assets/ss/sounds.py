"""Every sound event of the mod: sounds.json entries with subtitles, and the synthesised audio.

Each event has a recipe ``fn(rng, i) -> samples`` and a number of variations. The audio is written to
assets/spore_and_stem/sounds/<folder>/<name><i>.ogg. With ``synthesise=False`` (build.py --no-sounds) sounds.json is
still written and the existing .ogg files are kept.

Design: small creatures squeak and chirp through formant filters, puffballs and spores are soft lowpassed noise
bursts, wood and roots crackle with grains, big things get sub thumps and slow formant roars, and the glow side of the
mod (lumen spores, glowmoths, the Bloomreaver) adds a soft shimmer of high partials.
"""
from __future__ import annotations

import math

import numpy as np

from .out import Out
from .paths import MOD_ID, SOUNDS
from .synth import (Rng, bandpass, curve, decay, encode_ogg, finish, formant, grains, highpass, lowpass, mixdown,
                    n_of, noise, osc, pad, peak, reverb, smooth_env, time, tremolo)

# ---------------------------------------------------------------------------------------------- building blocks


def chirp(rng: Rng, f0: float, f1: float, dur: float, vowel: str = "i", shift: float = 2.2, vib: float = 0.0,
          shape: str = "saw") -> np.ndarray:
    """A small voiced squeak gliding from f0 to f1."""
    t = time(dur)
    f = curve(dur, (0, f0), (dur * 0.35, (f0 * 2 + f1) / 3), (dur, f1), shape="exp")
    if vib:
        f = f * (1 + vib * np.sin(2 * np.pi * rng.uniform(18, 26) * t))
    src = osc(f, shape)
    v = formant(src, vowel, shift)
    return v * smooth_env(dur, min(0.012, dur * 0.2), dur * 0.45)


def puff(rng: Rng, dur: float, bright: float = 1800.0, body: float = 260.0) -> np.ndarray:
    """A soft breathy burst of spores."""
    x = noise(dur, rng, "pink")
    x = lowpass(x, bright, 3)
    x = peak(x, body, 1.2, 1.5)
    env = curve(dur, (0, 0), (0.012, 1), (dur * 0.25, 0.55), (dur, 0))
    return x * env


def thump(dur: float, f0: float, f1: float, tau: float) -> np.ndarray:
    f = curve(dur, (0, f0), (dur, f1), shape="exp")
    return osc(f) * decay(dur, tau, 0.002)


def creak(rng: Rng, dur: float, f0: float, density: float = 60.0) -> np.ndarray:
    """A woody stretching creak: a slow glottal pulse train through resonances."""
    f = curve(dur, (0, f0), (dur * 0.5, f0 * rng.uniform(0.85, 1.2)), (dur, f0 * 0.8), shape="exp")
    src = osc(f, "pulse") * (0.6 + 0.4 * tremolo(dur, rng.uniform(7, 13), 0.7, rng))
    x = peak(bandpass(src, 200, 3200), 900, 0.6, 3)
    return x * smooth_env(dur, dur * 0.25, dur * 0.4)


def shimmer(rng: Rng, dur: float, base: float = 1800.0, count: int = 6) -> np.ndarray:
    """Soft glassy partials twinkling in and out (the glow motif)."""
    out = np.zeros(n_of(dur))
    for k in range(count):
        f = base * rng.uniform(0.9, 2.6)
        start = rng.uniform(0, dur * 0.5)
        length = rng.uniform(dur * 0.3, dur * 0.8)
        tone = osc(np.full(n_of(length), f)) * decay(length, length / 3, 0.01)
        i = n_of(start)
        j = min(len(out), i + len(tone))
        out[i:j] += tone[: j - i] * rng.uniform(0.3, 1.0)
    return out


def bubble(rng: Rng, f0: float, dur: float = 0.09) -> np.ndarray:
    """A wet bubble pop: a sine that sweeps up fast as it decays."""
    f = f0 * np.exp(time(dur) * rng.uniform(9, 16))
    return osc(f) * decay(dur, dur / 4, 0.002)


def groan(rng: Rng, dur: float, f0: float, vowel: str = "o", shift: float = 0.75, breath: float = 0.35,
          fall: float = 0.8) -> np.ndarray:
    t = time(dur)
    f = curve(dur, (0, f0 * 1.05), (dur * 0.3, f0 * 1.1), (dur, f0 * fall), shape="exp")
    f = f * (1 + 0.012 * np.sin(2 * np.pi * 5.2 * t)) * (1 + 0.02 * lowpass(rng.normal(len(t)), 8) * 4)
    src = osc(f, "saw") + breath * noise(dur, rng, "pink")
    v = formant(src, vowel, shift)
    return v * smooth_env(dur, dur * 0.18, dur * 0.4)


def roar(rng: Rng, dur: float, f0: float, vowel: str = "a", shift: float = 0.55) -> np.ndarray:
    """A big layered roar: two detuned formant voices, rasp and a sub."""
    t = time(dur)
    f = curve(dur, (0, f0 * 0.8), (dur * 0.2, f0 * 1.15), (dur * 0.7, f0), (dur, f0 * 0.7), shape="exp")
    rasp = 1 + 0.25 * lowpass(rng.normal(len(t)), 60) * 3
    v1 = formant(osc(f * rasp, "saw"), vowel, shift)
    v2 = formant(osc(f * 1.007 * rasp, "saw"), "o", shift * 0.9)
    hiss = bandpass(noise(dur, rng, "pink"), 300, 2500) * 0.35
    sub = osc(f * 0.5) * 0.6
    env = smooth_env(dur, dur * 0.12, dur * 0.45)
    return (v1 + v2 * 0.8 + hiss + sub) * env


def dirt(rng: Rng, dur: float, density: float = 260.0, lo: float = 300, hi: float = 4000) -> np.ndarray:
    env = smooth_env(dur, dur * 0.2, dur * 0.4)
    bed = lowpass(noise(dur, rng, "brown"), 900) * 0.5
    return (grains(dur, rng, density, 0.006, lo, hi, env) * 1.5 + bed) * env


def crackle(rng: Rng, dur: float, density: float = 90.0) -> np.ndarray:
    env = smooth_env(dur, 0.005, dur * 0.6)
    return grains(dur, rng, density, 0.003, 1200, 7000, env)


# ---------------------------------------------------------------------------------------------- recipes

def sporeling_ambient(rng, i):
    notes = [(rng.uniform(1100, 1400), rng.uniform(1500, 1900)) for _ in range(rng.choice([1, 2, 2, 3]))]
    parts, at = [], 0.0
    for f0, f1 in notes:
        d = rng.uniform(0.07, 0.12)
        parts.append((chirp(rng, f0, f1, d, rng.choice(["i", "e"]), 2.4, vib=0.01), at, 1.0))
        at += d + rng.uniform(0.04, 0.09)
    return reverb(mixdown(at + 0.1, *parts), 0.3, 0.1)


def sporeling_hurt(rng, i):
    return reverb(chirp(rng, rng.uniform(1900, 2200), rng.uniform(1100, 1300), 0.16, "e", 2.6, vib=0.02), 0.25, 0.1)


def sporeling_death(rng, i):
    s = chirp(rng, 1500, 600, 0.55, "u", 2.0, vib=0.015)
    return reverb(mixdown(0.9, (s, 0, 1.0), (puff(rng, 0.45, 2200), 0.38, 0.5)), 0.4, 0.15)


def sporeling_sneeze(rng, i):
    inhale = chirp(rng, 900, 1500, 0.22, "a", 2.0) * 0.4 + highpass(noise(0.22, rng), 2500) * 0.15 * curve(0.22, (0, 0), (0.22, 1))
    choo = puff(rng, 0.28, 3200, 600) * 1.4
    pip = chirp(rng, 1700, 1300, 0.07, "i", 2.6)
    return reverb(mixdown(0.75, (inhale, 0, 0.7), (choo, 0.26, 1.0), (pip, 0.27, 0.6)), 0.35, 0.12)


def sporeling_happy(rng, i):
    parts, at = [], 0.0
    base = rng.uniform(1050, 1250)
    for k in range(4):
        f = base * (1.12 ** k)
        parts.append((chirp(rng, f, f * 1.25, 0.08, "i", 2.5), at, 1.0))
        at += 0.085
    parts.append((shimmer(rng, 0.5, 2400, 4) * 0.25, 0.1, 1.0))
    return reverb(mixdown(at + 0.4, *parts), 0.35, 0.12)


def bloatshroom_ambient(rng, i):
    parts = [(lowpass(noise(0.9, rng, "brown"), 400) * smooth_env(0.9, 0.3, 0.4) * 0.6, 0, 1.0)]
    for k in range(rng.choice([3, 4, 5])):
        parts.append((bubble(rng, rng.uniform(140, 260), 0.12), rng.uniform(0.05, 0.75), rng.uniform(0.5, 1.0)))
    return reverb(mixdown(1.0, *parts), 0.3, 0.12)


def bloatshroom_hurt(rng, i):
    return mixdown(0.4, (thump(0.3, 180, 90, 0.07), 0, 1.0), (puff(rng, 0.25, 900, 220), 0.0, 0.8),
                   (bubble(rng, 200, 0.1), 0.05, 0.7))


def bloatshroom_death(rng, i):
    hiss = bandpass(noise(1.0, rng, "pink"), 600, 5000) * curve(1.0, (0, 0), (0.05, 1), (1.0, 0))
    hiss = spectral_sweep(hiss, 5000, 900)
    return reverb(mixdown(1.2, (hiss, 0, 0.8), (thump(0.4, 120, 60, 0.12), 0.8, 1.0)), 0.4, 0.15)


def spectral_sweep(x, f0, f1):
    """Crossfades a few lowpass versions so the brightness glides from f0 to f1 over the sound."""
    stages = [lowpass(x, f) for f in np.geomspace(f0, f1, 5)]
    n = len(x)
    pos = np.linspace(0, len(stages) - 1, n)
    out = np.zeros(n)
    for k, s in enumerate(stages):
        w = np.clip(1 - np.abs(pos - k), 0, 1)
        out += s * w
    return out


def bloatshroom_swell(rng, i):
    d = 1.5
    stretch = creak(rng, d, rng.uniform(26, 32), 40) * curve(d, (0, 0.2), (d, 1.0))
    air = bandpass(noise(d, rng, "pink"), 300, 1500) * curve(d, (0, 0), (d * 0.9, 0.7), (d, 0.4))
    rising = osc(curve(d, (0, 90), (d, 260), shape="exp")) * curve(d, (0, 0), (d, 0.35))
    return mixdown(d, (stretch, 0, 0.7), (air, 0, 0.6), (rising, 0, 0.6))


def bloatshroom_burst(rng, i):
    big = puff(rng, 1.1, 2400, 220) * 1.6
    sub = thump(0.5, 110, 40, 0.15)
    pops = [(bubble(rng, rng.uniform(300, 700), 0.06), rng.uniform(0.0, 0.2), 0.5) for _ in range(5)]
    return reverb(mixdown(1.4, (big, 0, 1.0), (sub, 0, 1.2), *pops), 0.8, 0.22)


def shambler_ambient(rng, i):
    g = groan(rng, rng.uniform(1.0, 1.5), rng.uniform(85, 110), rng.choice(["o", "u", "uh"]), 0.8, breath=0.2)
    return reverb(mixdown(len(g) / 44100 + 0.2, (g, 0, 1.0), (creak(rng, 0.6, 30) * 0.4, rng.uniform(0.2, 0.6), 1.0)),
                  0.6, 0.2)


def shambler_hurt(rng, i):
    g = groan(rng, 0.35, rng.uniform(130, 150), "uh", 0.85, fall=0.7)
    return mixdown(0.45, (g, 0, 1.0), (crackle(rng, 0.25, 120), 0.0, 0.5))


def shambler_death(rng, i):
    g = groan(rng, 1.6, 110, "o", 0.78, fall=0.55)
    return reverb(mixdown(2.1, (g, 0, 1.0), (crackle(rng, 0.9, 160), 0.9, 0.6), (thump(0.5, 140, 60, 0.12), 1.3, 0.8),
                          (puff(rng, 0.8, 1600), 1.3, 0.4)), 0.7, 0.2)


def shambler_attack(rng, i):
    whoosh = spectral_sweep(bandpass(noise(0.35, rng, "pink"), 200, 3000), 600, 3000) * smooth_env(0.35, 0.2, 0.1)
    return mixdown(0.5, (whoosh, 0, 0.8), (groan(rng, 0.3, 150, "a", 0.85), 0.0, 0.6), (thump(0.2, 200, 90, 0.05), 0.3, 0.6))


def shambler_rise(rng, i):
    return reverb(mixdown(2.0, (crackle(rng, 1.2, 220), 0, 0.7), (dirt(rng, 1.0), 0.0, 0.6),
                          (groan(rng, 1.2, 70, "u", 0.75, fall=1.3), 0.6, 1.0)), 0.6, 0.2)


def sporemaw_ambient(rng, i):
    d = rng.uniform(0.8, 1.1)
    breath = bandpass(noise(d, rng, "pink"), 400, 2500) * (0.5 + 0.5 * tremolo(d, 2.2, 0.8, rng)) * smooth_env(d, 0.2, 0.3)
    clicks = grains(d, rng, 14, 0.002, 1500, 5000)
    return reverb(mixdown(d + 0.1, (breath, 0, 0.6), (clicks, 0, 1.2)), 0.4, 0.15)


def sporemaw_hurt(rng, i):
    hiss = bandpass(noise(0.3, rng), 1500, 6000) * decay(0.3, 0.08)
    squeal = chirp(rng, 900, 650, 0.25, "a", 1.4)
    return mixdown(0.35, (hiss, 0, 0.6), (squeal, 0, 0.9))


def sporemaw_death(rng, i):
    gurgle = [(bubble(rng, rng.uniform(90, 200), 0.12), k * 0.09 + rng.uniform(0, 0.03), 1 - k * 0.07) for k in range(10)]
    return reverb(mixdown(1.4, (groan(rng, 0.9, 120, "u", 1.0, 0.6, fall=0.6), 0, 0.8), *gurgle,
                          (dirt(rng, 0.6), 0.7, 0.6)), 0.5, 0.15)


def sporemaw_emerge(rng, i):
    return reverb(mixdown(1.0, (dirt(rng, 0.9, 340), 0, 1.0), (creak(rng, 0.5, 42) * 0.5, 0.35, 1.0),
                          (thump(0.3, 90, 50, 0.1), 0.0, 0.6)), 0.4, 0.15)


def sporemaw_burrow(rng, i):
    d = dirt(rng, 0.8, 300)[::-1].copy()
    return reverb(mixdown(0.9, (d, 0, 1.0), (thump(0.3, 70, 40, 0.1), 0.6, 0.7)), 0.4, 0.15)


def sporemaw_spit(rng, i):
    pop = thump(0.12, rng.uniform(260, 320), 120, 0.03)
    wet = puff(rng, 0.3, 2600, 500)
    return mixdown(0.4, (pop, 0, 1.0), (wet, 0.02, 0.9), (bubble(rng, 400, 0.07), 0.04, 0.5))


def click_train(rng, dur, rate, lo=2500, hi=7000, jitter=0.3):
    out = np.zeros(n_of(dur))
    t = 0.0
    while t < dur:
        c = bandpass(rng.normal(n_of(0.004)) * np.hanning(n_of(0.004)), lo, hi)
        i = n_of(t)
        j = min(len(out), i + len(c))
        out[i:j] += c[: j - i] * rng.uniform(0.5, 1.0)
        t += (1 / rate) * rng.uniform(1 - jitter, 1 + jitter)
    return out


def mimicap_ambient(rng, i):
    d = rng.uniform(0.4, 0.7)
    return reverb(click_train(rng, d, rng.uniform(22, 34)) * smooth_env(d, 0.05, 0.2), 0.3, 0.1)


def mimicap_hurt(rng, i):
    return mixdown(0.4, (click_train(rng, 0.3, 45) * decay(0.3, 0.12), 0, 1.0),
                   (chirp(rng, 1300, 900, 0.18, "e", 1.6, shape="pulse"), 0, 0.6))


def mimicap_death(rng, i):
    d = 1.0
    rattle = click_train(rng, d, 40) * curve(d, (0, 1), (d, 0))
    return reverb(mixdown(1.2, (rattle, 0, 1.0), (chirp(rng, 1100, 380, 0.7, "u", 1.4, shape="pulse"), 0.05, 0.5)), 0.4, 0.15)


def mimicap_wake(rng, i):
    snaps = [(click_train(rng, 0.03, 200, 1500, 6000), t, 1.0) for t in (0.0, 0.11, 0.19, 0.24, 0.3)]
    unfold = creak(rng, 0.45, 55) * 0.6
    return reverb(mixdown(0.7, *snaps, (unfold, 0.05, 1.0), (chirp(rng, 600, 1100, 0.2, "a", 1.5, shape="pulse"), 0.35, 0.5)),
                  0.35, 0.12)


def mimicap_bite(rng, i):
    chomp1 = bandpass(rng.normal(n_of(0.02)), 800, 5000) * decay(0.02, 0.005)
    chomp2 = bandpass(rng.normal(n_of(0.03)), 500, 4000) * decay(0.03, 0.008)
    return mixdown(0.25, (chomp1, 0, 1.0), (chomp2, 0.07, 1.0), (thump(0.12, 160, 80, 0.03), 0.07, 0.8))


def mimicap_step(rng, i):
    return mixdown(0.08, (click_train(rng, 0.012, 300, 1800, 5000), 0, 1.0), (thump(0.05, 220, 120, 0.01), 0, 0.3))


def glowmoth_ambient(rng, i):
    d = rng.uniform(0.7, 1.0)
    flutter = bandpass(noise(d, rng, "pink"), 150, 1200) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * rng.uniform(22, 28) * time(d))))
    return reverb(mixdown(d, (flutter * smooth_env(d, 0.15, 0.3), 0, 0.7), (shimmer(rng, d, 2600, 4), 0, 0.12)), 0.4, 0.15)


def glowmoth_hurt(rng, i):
    return chirp(rng, 2600, 2000, 0.09, "i", 3.0)


def glowmoth_death(rng, i):
    return reverb(mixdown(0.9, (chirp(rng, 2400, 900, 0.3, "i", 2.8), 0, 0.6), (shimmer(rng, 0.8, 2000, 7), 0.05, 0.35)),
                  0.5, 0.2)


def truffler_ambient(rng, i):
    d = rng.uniform(0.25, 0.4)
    grunt = groan(rng, d, rng.uniform(150, 190), "uh", 1.05, 0.6, fall=0.85)
    nose = bandpass(noise(d, rng), 800, 3500) * smooth_env(d, 0.02, 0.1) * 0.4
    parts = [(grunt + nose, 0, 1.0)]
    if rng.uniform() < 0.6:
        parts.append((groan(rng, 0.2, 170, "o", 1.05, 0.5), d + 0.08, 0.8))
    return reverb(mixdown(d * 2 + 0.2, *parts), 0.3, 0.1)


def truffler_hurt(rng, i):
    return groan(rng, 0.3, 260, "e", 1.15, 0.5, fall=1.25)


def truffler_death(rng, i):
    return reverb(groan(rng, 0.9, 160, "o", 1.0, 0.5, fall=0.55), 0.5, 0.15)


def truffler_sniff(rng, i):
    parts = []
    for k in range(rng.choice([2, 3])):
        s = bandpass(noise(0.08, rng), 1200, 5000) * smooth_env(0.08, 0.01, 0.05)
        parts.append((s, k * 0.13, 1.0))
    return mixdown(0.45, *parts)


def truffler_dig(rng, i):
    return mixdown(0.6, (dirt(rng, 0.5, 400, 400, 5000), 0, 1.0), (thump(0.1, 140, 80, 0.03), 0.05, 0.5))


def myceliarch_ambient(rng, i):
    d = rng.uniform(2.0, 2.6)
    rumble = lowpass(noise(d, rng, "brown"), 180) * smooth_env(d, 0.6, 0.8)
    voice = groan(rng, d * 0.8, rng.uniform(48, 58), "o", 0.55, 0.4, fall=0.85)
    return reverb(mixdown(d, (rumble, 0, 0.8), (voice, d * 0.1, 0.9), (creak(rng, 0.8, 24) * 0.5, d * 0.4, 1.0)), 1.2, 0.3)


def myceliarch_hurt(rng, i):
    return reverb(mixdown(0.8, (roar(rng, 0.5, rng.uniform(70, 85), "uh", 0.6), 0, 1.0), (crackle(rng, 0.3, 200), 0, 0.6)),
                  0.8, 0.25)


def myceliarch_death(rng, i):
    d = 4.0
    return reverb(mixdown(d, (roar(rng, 2.4, 62, "a", 0.55), 0, 1.0), (crackle(rng, 2.2, 260), 1.2, 0.7),
                          (dirt(rng, 1.6, 300), 1.8, 0.6), (puff(rng, 1.8, 1800), 2.0, 0.7),
                          (thump(0.9, 70, 30, 0.3), 2.4, 1.2)), 1.5, 0.3)


def myceliarch_roar(rng, i):
    return reverb(mixdown(3.0, (roar(rng, 2.4, rng.uniform(55, 64), "a", 0.52), 0, 1.0),
                          (shimmer(rng, 2.0, 1500, 8) * 0.12, 0.3, 1.0)), 1.6, 0.3)


def myceliarch_slam(rng, i):
    return reverb(mixdown(1.4, (thump(0.8, 90, 28, 0.28), 0, 1.5), (crackle(rng, 0.5, 300), 0, 0.8),
                          (dirt(rng, 0.9, 380), 0.05, 0.8)), 1.0, 0.3)


def myceliarch_spore_nova(rng, i):
    d = 2.2
    inhale = spectral_sweep(bandpass(noise(0.8, rng, "pink"), 200, 4000), 500, 3000) * curve(0.8, (0, 0), (0.8, 1))
    blast = puff(rng, 1.4, 3000, 260) * 1.8
    return reverb(mixdown(d, (inhale, 0, 0.6), (blast, 0.75, 1.0), (thump(0.6, 80, 35, 0.2), 0.75, 1.0),
                          (shimmer(rng, 1.2, 1700, 10) * 0.2, 0.8, 1.0)), 1.2, 0.3)


def myceliarch_root_erupt(rng, i):
    return reverb(mixdown(1.0, (crackle(rng, 0.5, 400), 0, 1.0), (thump(0.4, 120, 45, 0.12), 0, 1.0), (dirt(rng, 0.6, 360), 0, 0.7)),
                  0.6, 0.2)


def myceliarch_step(rng, i):
    return mixdown(0.6, (thump(0.5, 70, 32, 0.14), 0, 1.4), (dirt(rng, 0.3, 200), 0, 0.4))


def myceliarch_emerge(rng, i):
    d = 3.5
    rumble = lowpass(noise(d, rng, "brown"), 160) * curve(d, (0, 0), (d * 0.8, 1), (d, 0.3))
    return reverb(mixdown(d, (rumble, 0, 1.0), (crackle(rng, 2.5, 200) * curve(2.5, (0, 0.2), (2.5, 1)), 0.5, 0.8),
                          (dirt(rng, 2.0, 300), 1.0, 0.7), (roar(rng, 1.4, 52, "o", 0.55), 2.1, 0.8)), 1.4, 0.3)


def root_spike_erupt(rng, i):
    return mixdown(0.5, (crackle(rng, 0.25, 500), 0, 1.0), (thump(0.25, 160, 70, 0.06), 0, 0.9), (dirt(rng, 0.35, 380), 0.02, 0.6))


def spore_glob_splat(rng, i):
    return mixdown(0.35, (puff(rng, 0.3, 1800, 400), 0, 1.0), (bubble(rng, rng.uniform(250, 350), 0.08), 0, 0.7),
                   (bubble(rng, rng.uniform(400, 600), 0.06), 0.04, 0.4))


def spore_bomb_burst(rng, i):
    return reverb(mixdown(0.9, (puff(rng, 0.8, 2600, 300) * 1.4, 0, 1.0), (thump(0.3, 140, 60, 0.08), 0, 0.8)), 0.6, 0.2)


def spore_bomb_throw(rng, i):
    w = spectral_sweep(bandpass(noise(0.3, rng, "pink"), 300, 4000), 800, 3500) * smooth_env(0.3, 0.12, 0.15)
    return w


def bloomreaver_burst(rng, i):
    whoosh = spectral_sweep(bandpass(noise(0.6, rng, "pink"), 200, 5000), 4000, 700) * smooth_env(0.6, 0.02, 0.4)
    return reverb(mixdown(1.1, (whoosh, 0, 1.0), (puff(rng, 0.6, 2400), 0, 0.8), (shimmer(rng, 0.9, 2000, 9), 0.0, 0.25),
                          (thump(0.3, 110, 50, 0.08), 0, 0.7)), 0.8, 0.25)


def fruiting_heart_use(rng, i):
    beat = mixdown(0.6, (thump(0.18, 75, 45, 0.06), 0, 1.0), (thump(0.18, 70, 42, 0.06), 0.22, 0.8))
    swell = osc(curve(1.4, (0, 220), (1.4, 440), shape="exp")) * curve(1.4, (0, 0), (1.2, 0.3), (1.4, 0)) * 0.4
    return reverb(mixdown(1.6, (beat, 0, 1.0), (swell, 0.1, 1.0), (shimmer(rng, 1.2, 1500, 8), 0.2, 0.25)), 0.9, 0.3)


def bouncecap_bounce(rng, i):
    d = 0.45
    f = curve(d, (0, rng.uniform(170, 200)), (0.05, rng.uniform(320, 380)), (d, rng.uniform(250, 280)), shape="exp")
    f = f * (1 + 0.06 * np.sin(2 * np.pi * 14 * time(d)) * np.exp(-time(d) / 0.15))
    boing = formant(osc(f, "tri") + 0.3 * osc(f, "saw"), "o", 1.1) * decay(d, 0.14, 0.004)
    return mixdown(0.5, (boing, 0, 1.0), (puff(rng, 0.12, 1500, 300), 0, 0.3))


def giant_puffball_puff(rng, i):
    return reverb(puff(rng, 0.55, 2000, 260), 0.4, 0.15)


def cultivation_log_inoculate(rng, i):
    sprinkle = grains(0.6, rng, 90, 0.002, 3000, 9000, smooth_env(0.6, 0.05, 0.3))
    return reverb(mixdown(0.8, (sprinkle, 0, 0.8), (puff(rng, 0.4, 2400, 400), 0.02, 0.4), (shimmer(rng, 0.6, 2200, 4), 0.05, 0.15)),
                  0.4, 0.15)


def cultivation_log_harvest(rng, i):
    pops = [(bubble(rng, rng.uniform(380, 620), 0.07), k * rng.uniform(0.07, 0.11), 1.0) for k in range(3)]
    return mixdown(0.45, *pops, (puff(rng, 0.25, 1800, 400), 0, 0.3))


def mycelial_veil_pick(rng, i):
    return reverb(mixdown(0.6, (bubble(rng, 520, 0.08), 0, 0.9), (shimmer(rng, 0.5, 2600, 5), 0.01, 0.4)), 0.4, 0.15)


# ---------------------------------------------------------------------------------------------- the event table

# event -> (recipe, variations, subtitle, loudness dB RMS, extra per-sound fields)
LOUD = {"attenuation_distance": 48}
EVENTS = {
    "entity.sporeling.ambient": (sporeling_ambient, 4, "Sporeling chirps", -22, {}),
    "entity.sporeling.hurt": (sporeling_hurt, 3, "Sporeling squeaks", -19, {}),
    "entity.sporeling.death": (sporeling_death, 2, "Sporeling dies", -20, {}),
    "entity.sporeling.sneeze": (sporeling_sneeze, 3, "Sporeling sneezes", -20, {}),
    "entity.sporeling.happy": (sporeling_happy, 2, "Sporeling trills", -21, {}),
    "entity.bloatshroom.ambient": (bloatshroom_ambient, 4, "Bloatshroom gurgles", -22, {}),
    "entity.bloatshroom.hurt": (bloatshroom_hurt, 3, "Bloatshroom hurts", -18, {}),
    "entity.bloatshroom.death": (bloatshroom_death, 2, "Bloatshroom deflates", -19, {}),
    "entity.bloatshroom.swell": (bloatshroom_swell, 2, "Bloatshroom swells", -18, {}),
    "entity.bloatshroom.burst": (bloatshroom_burst, 3, "Bloatshroom bursts", -14, {}),
    "entity.shambler.ambient": (shambler_ambient, 4, "Shambler groans", -20, {}),
    "entity.shambler.hurt": (shambler_hurt, 3, "Shambler hurts", -18, {}),
    "entity.shambler.death": (shambler_death, 2, "Shambler dies", -18, {}),
    "entity.shambler.attack": (shambler_attack, 3, "Shambler swipes", -18, {}),
    "entity.shambler.rise": (shambler_rise, 2, "Shambler rises", -17, {}),
    "entity.sporemaw.ambient": (sporemaw_ambient, 4, "Sporemaw breathes", -23, {}),
    "entity.sporemaw.hurt": (sporemaw_hurt, 3, "Sporemaw hisses", -18, {}),
    "entity.sporemaw.death": (sporemaw_death, 2, "Sporemaw dies", -19, {}),
    "entity.sporemaw.emerge": (sporemaw_emerge, 2, "Sporemaw emerges", -18, {}),
    "entity.sporemaw.burrow": (sporemaw_burrow, 2, "Sporemaw burrows", -19, {}),
    "entity.sporemaw.spit": (sporemaw_spit, 3, "Sporemaw spits", -17, {}),
    "entity.mimicap.ambient": (mimicap_ambient, 4, "Mimicap chitters", -24, {}),
    "entity.mimicap.hurt": (mimicap_hurt, 3, "Mimicap shrieks", -18, {}),
    "entity.mimicap.death": (mimicap_death, 2, "Mimicap dies", -19, {}),
    "entity.mimicap.wake": (mimicap_wake, 2, "Mimicap unfolds", -16, {}),
    "entity.mimicap.bite": (mimicap_bite, 3, "Mimicap bites", -16, {}),
    "entity.mimicap.step": (mimicap_step, 4, "Mimicap skitters", -26, {}),
    "entity.glowmoth.ambient": (glowmoth_ambient, 3, "Glowmoth flutters", -26, {}),
    "entity.glowmoth.hurt": (glowmoth_hurt, 2, "Glowmoth hurts", -22, {}),
    "entity.glowmoth.death": (glowmoth_death, 2, "Glowmoth dies", -22, {}),
    "entity.truffler.ambient": (truffler_ambient, 4, "Truffler grunts", -21, {}),
    "entity.truffler.hurt": (truffler_hurt, 3, "Truffler squeals", -18, {}),
    "entity.truffler.death": (truffler_death, 2, "Truffler dies", -19, {}),
    "entity.truffler.sniff": (truffler_sniff, 3, "Truffler sniffs", -22, {}),
    "entity.truffler.dig": (truffler_dig, 3, "Truffler digs", -20, {}),
    "entity.myceliarch.ambient": (myceliarch_ambient, 3, "Myceliarch rumbles", -18, LOUD),
    "entity.myceliarch.hurt": (myceliarch_hurt, 3, "Myceliarch hurts", -16, LOUD),
    "entity.myceliarch.death": (myceliarch_death, 1, "Myceliarch falls", -14, {"attenuation_distance": 96}),
    "entity.myceliarch.roar": (myceliarch_roar, 2, "Myceliarch roars", -13, {"attenuation_distance": 96}),
    "entity.myceliarch.slam": (myceliarch_slam, 2, "Myceliarch slams", -13, LOUD),
    "entity.myceliarch.spore_nova": (myceliarch_spore_nova, 2, "Spore Nova bursts", -14, LOUD),
    "entity.myceliarch.root_erupt": (myceliarch_root_erupt, 2, "Roots erupt", -15, LOUD),
    "entity.myceliarch.step": (myceliarch_step, 3, "Heavy footsteps", -17, LOUD),
    "entity.myceliarch.emerge": (myceliarch_emerge, 1, "The Myceliarch emerges", -14, {"attenuation_distance": 96}),
    "entity.root_spike.erupt": (root_spike_erupt, 3, "Root erupts", -16, {}),
    "entity.spore_glob.splat": (spore_glob_splat, 3, "Spore glob splats", -18, {}),
    "entity.spore_bomb.burst": (spore_bomb_burst, 2, "Spore Bomb bursts", -15, {}),
    "item.spore_bomb.throw": (spore_bomb_throw, 2, "Spore Bomb flies", -21, {}),
    "item.bloomreaver.burst": (bloomreaver_burst, 2, "Spore Burst", -15, {}),
    "item.fruiting_heart.use": (fruiting_heart_use, 1, "Fruiting Heart beats", -16, {}),
    "block.bouncecap.bounce": (bouncecap_bounce, 3, "Bouncecap boings", -18, {}),
    "block.giant_puffball.puff": (giant_puffball_puff, 3, "Puffball puffs", -19, {}),
    "block.cultivation_log.inoculate": (cultivation_log_inoculate, 2, "Log inoculated", -21, {}),
    "block.cultivation_log.harvest": (cultivation_log_harvest, 2, "Mushrooms harvested", -19, {}),
    "block.mycelial_veil.pick": (mycelial_veil_pick, 2, "Bulb picked", -20, {}),
}


def file_of(event: str, i: int) -> str:
    """'entity.sporeling.ambient', 2 -> 'entity/sporeling/ambient2'."""
    kind, owner, name = event.split(".", 2)
    return f"{kind}/{owner}/{name.replace('.', '_')}{i}"


def generate(out: Out, synthesise: bool = True) -> None:
    for e_index, (event, (recipe, variants, subtitle, loud, extra)) in enumerate(EVENTS.items()):
        entries = []
        for i in range(1, variants + 1):
            rel = file_of(event, i)
            entry = {"name": f"{MOD_ID}:{rel}"}
            entry.update(extra)
            entries.append(entry if len(entry) > 1 else entry["name"])
            path = SOUNDS / f"{rel}.ogg"
            if synthesise or not path.exists():
                rng = Rng(e_index * 1000 + i * 17 + 12345)
                samples = finish(np.asarray(recipe(rng, i), dtype=np.float64), rms_db=loud)
                encode_ogg(samples, path)
        out.sound(event, entries, subtitle)
