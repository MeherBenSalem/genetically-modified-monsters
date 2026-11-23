package com.nightbeam.sporeandstem.neoforge;

import com.nightbeam.sporeandstem.client.ModClient;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterParticleProvidersEvent;

/** Client-only wiring. Block render layers come from each model's render_type on NeoForge. */
public final class SporeAndStemNeoForgeClient {

    private SporeAndStemNeoForgeClient() {
    }

    static void init(IEventBus modBus) {
        modBus.addListener(SporeAndStemNeoForgeClient::onParticles);
        modBus.addListener(SporeAndStemNeoForgeClient::onRenderers);
        modBus.addListener(SporeAndStemNeoForgeClient::onLayers);
    }

    private static void onParticles(RegisterParticleProvidersEvent event) {
        ModClient.registerParticles((type, provider) -> event.registerSpriteSet(type, provider::apply));
    }

    private static void onRenderers(EntityRenderersEvent.RegisterRenderers event) {
        ModClient.registerRenderers(event::registerEntityRenderer);
    }

    private static void onLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
        ModClient.registerLayers(event::registerLayerDefinition);
    }
}
