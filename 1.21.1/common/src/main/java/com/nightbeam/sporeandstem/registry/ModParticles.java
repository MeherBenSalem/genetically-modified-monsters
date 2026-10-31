package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.platform.Services;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.Registries;

/** Particle types. Sprites and providers are registered per loader from {@code client.ModParticleProviders}. */
public final class ModParticles {
    /** A drifting pale spore mote. */
    public static final RegistryEntry<SimpleParticleType> SPORE = particle("spore");
    /** A luminous teal spore, drawn at full brightness. */
    public static final RegistryEntry<SimpleParticleType> GLOW_SPORE = particle("glow_spore");
    /** A drop of ink falling from an Inkcap's fringe. */
    public static final RegistryEntry<SimpleParticleType> INK_DRIP = particle("ink_drip");

    private ModParticles() {
    }

    private static RegistryEntry<SimpleParticleType> particle(String name) {
        return Services.REGISTRAR.register(Registries.PARTICLE_TYPE, name, () -> new Type(false));
    }

    public static void init() {
    }

    /** SimpleParticleType's constructor is protected. */
    private static final class Type extends SimpleParticleType {
        private Type(boolean overrideLimiter) {
            super(overrideLimiter);
        }
    }
}
