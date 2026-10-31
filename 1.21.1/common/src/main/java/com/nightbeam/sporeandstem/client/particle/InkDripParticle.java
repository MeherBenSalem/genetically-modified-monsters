package com.nightbeam.sporeandstem.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;

/** A drop of ink: hangs for a moment, falls, and splats out on landing. */
public class InkDripParticle extends TextureSheetParticle {
    private int hang;

    protected InkDripParticle(ClientLevel level, double x, double y, double z, SpriteSet sprites) {
        super(level, x, y, z);
        this.pickSprite(sprites);
        this.quadSize = 0.06F;
        this.gravity = 0.0F;
        this.hang = 10 + this.random.nextInt(10);
        this.lifetime = 80;
        this.xd = this.yd = this.zd = 0.0;
        this.hasPhysics = true;
    }

    @Override
    public void tick() {
        if (this.hang > 0 && --this.hang == 0) {
            this.gravity = 0.06F;
        }
        super.tick();
        if (this.onGround) {
            this.remove();
        }
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_OPAQUE;
    }

    public static ParticleProvider<SimpleParticleType> provider(SpriteSet sprites) {
        return (type, level, x, y, z, dx, dy, dz) -> new InkDripParticle(level, x, y, z, sprites);
    }
}
