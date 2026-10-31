package com.nightbeam.sporeandstem.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;

/** Spore motes: drift and sway slowly, fade out. The glowing kind is drawn at full brightness. */
public class SporeParticle extends TextureSheetParticle {
    private final SpriteSet sprites;
    private final boolean glowing;
    private final float swayPhase;

    protected SporeParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz,
                            SpriteSet sprites, boolean glowing) {
        super(level, x, y, z, dx, dy, dz);
        this.sprites = sprites;
        this.glowing = glowing;
        this.friction = 0.94F;
        this.gravity = glowing ? -0.004F : 0.003F;
        this.xd = dx + (this.random.nextDouble() - 0.5) * 0.01;
        this.yd = dy + (glowing ? 0.004 : 0.0);
        this.zd = dz + (this.random.nextDouble() - 0.5) * 0.01;
        this.quadSize = 0.05F + this.random.nextFloat() * 0.05F;
        this.lifetime = 40 + this.random.nextInt(50);
        this.swayPhase = this.random.nextFloat() * Mth.TWO_PI;
        this.hasPhysics = true;
        this.setSpriteFromAge(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.removed) {
            float t = (this.age + this.swayPhase * 10.0F) * 0.15F;
            this.xd += Mth.sin(t) * 0.0012;
            this.zd += Mth.cos(t * 0.8F) * 0.0012;
            this.alpha = Mth.clamp(1.0F - (float) this.age / this.lifetime, 0.0F, 1.0F) * 0.9F;
            this.setSpriteFromAge(this.sprites);
        }
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
    }

    @Override
    protected int getLightColor(float partialTick) {
        return glowing ? 0xF000F0 : super.getLightColor(partialTick);
    }

    public static ParticleProvider<SimpleParticleType> spore(SpriteSet sprites) {
        return (type, level, x, y, z, dx, dy, dz) -> new SporeParticle(level, x, y, z, dx, dy, dz, sprites, false);
    }

    public static ParticleProvider<SimpleParticleType> glow(SpriteSet sprites) {
        return (type, level, x, y, z, dx, dy, dz) -> new SporeParticle(level, x, y, z, dx, dy, dz, sprites, true);
    }
}
