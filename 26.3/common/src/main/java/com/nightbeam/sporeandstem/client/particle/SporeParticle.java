package com.nightbeam.sporeandstem.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;

/** Spore motes: drift and sway slowly, fade out. The glowing kind is drawn at full brightness. */
public class SporeParticle extends SingleQuadParticle {
    private final SpriteSet sprites;
    private final boolean glowing;
    private final float swayPhase;

    protected SporeParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz,
                            SpriteSet sprites, boolean glowing, RandomSource random) {
        super(level, x, y, z, sprites.first());
        this.sprites = sprites;
        this.glowing = glowing;
        this.friction = 0.94F;
        this.gravity = glowing ? -0.004F : 0.003F;
        this.xd = dx + (random.nextDouble() - 0.5) * 0.01;
        this.yd = dy + (glowing ? 0.004 : 0.0);
        this.zd = dz + (random.nextDouble() - 0.5) * 0.01;
        this.quadSize = 0.05F + random.nextFloat() * 0.05F;
        this.lifetime = 40 + random.nextInt(50);
        this.swayPhase = random.nextFloat() * Mth.TWO_PI;
        this.hasPhysics = true;
        this.setSprite(sprites.get(this.age, this.lifetime));
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.removed) {
            float t = (this.age + this.swayPhase * 10.0F) * 0.15F;
            this.xd += Mth.sin(t) * 0.0012;
            this.zd += Mth.cos(t * 0.8F) * 0.0012;
            this.alpha = Mth.clamp(1.0F - (float) this.age / this.lifetime, 0.0F, 1.0F) * 0.9F;
            this.setSprite(this.sprites.get(this.age, this.lifetime));
        }
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    @Override
    protected int getLightCoords(float partialTick) {
        return glowing ? 0xF000F0 : super.getLightCoords(partialTick);
    }

    public static ParticleProvider<SimpleParticleType> spore(SpriteSet sprites) {
        return (type, level, x, y, z, dx, dy, dz, random) -> new SporeParticle(level, x, y, z, dx, dy, dz, sprites, false, random);
    }

    public static ParticleProvider<SimpleParticleType> glow(SpriteSet sprites) {
        return (type, level, x, y, z, dx, dy, dz, random) -> new SporeParticle(level, x, y, z, dx, dy, dz, sprites, true, random);
    }
}
