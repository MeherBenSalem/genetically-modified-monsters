package com.nightbeam.sporeandstem.forge;

import com.nightbeam.sporeandstem.client.ModClient;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import net.minecraftforge.eventbus.api.IEventBus;

/** Client-only wiring. Block render layers come from each model's render_type on Forge. */
public final class SporeAndStemForgeClient {

    private SporeAndStemForgeClient() {
    }

    static void init(IEventBus modBus) {
        modBus.addListener(SporeAndStemForgeClient::onParticles);
        modBus.addListener(SporeAndStemForgeClient::onRenderers);
        modBus.addListener(SporeAndStemForgeClient::onLayers);
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
