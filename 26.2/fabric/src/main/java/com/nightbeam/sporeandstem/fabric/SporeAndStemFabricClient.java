package com.nightbeam.sporeandstem.fabric;

import com.nightbeam.sporeandstem.client.ModClient;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.particle.v1.ParticleProviderRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;

/** Block render layers are inferred from texture transparency in 26.x, so there is nothing to map. */
public class SporeAndStemFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        ModClient.registerParticles((type, provider) -> ParticleProviderRegistry.getInstance().register(type, provider::apply));
        ModClient.registerLayers((layer, definition) -> ModelLayerRegistry.registerModelLayer(layer, definition::get));
        ModClient.registerRenderers(EntityRendererRegistry::register);
    }
}
