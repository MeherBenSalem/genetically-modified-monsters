package com.nightbeam.sporeandstem.client;

import com.nightbeam.sporeandstem.client.particle.InkDripParticle;
import com.nightbeam.sporeandstem.client.particle.SporeParticle;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModParticles;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;

import java.util.function.Function;
import java.util.function.Supplier;

/** Client wiring shared by both loaders. Each loader hands in its own registration callbacks. */
public final class ModClient {

    private ModClient() {
    }

    public interface ParticleSink {
        void register(ParticleType<SimpleParticleType> type, Function<SpriteSet, ParticleProvider<SimpleParticleType>> provider);
    }

    public interface RendererSink {
        <T extends Entity> void register(EntityType<? extends T> type, EntityRendererProvider<T> provider);
    }

    public interface LayerSink {
        void register(ModelLayerLocation layer, Supplier<LayerDefinition> definition);
    }

    public static void registerParticles(ParticleSink sink) {
        sink.register(ModParticles.SPORE.get(), SporeParticle::spore);
        sink.register(ModParticles.GLOW_SPORE.get(), SporeParticle::glow);
        sink.register(ModParticles.INK_DRIP.get(), InkDripParticle::provider);
    }

    public static void registerRenderers(RendererSink sink) {
        sink.register(ModEntities.SPORE_BOMB.get(), ThrownItemRenderer::new);
        sink.register(ModEntities.SPORE_GLOB.get(), ThrownItemRenderer::new);
        ModEntityRenderers.register(sink);
    }

    public static void registerLayers(LayerSink sink) {
        ModEntityRenderers.registerLayers(sink);
    }
}
