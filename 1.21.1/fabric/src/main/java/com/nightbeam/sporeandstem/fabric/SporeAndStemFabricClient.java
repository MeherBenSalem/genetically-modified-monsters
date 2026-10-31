package com.nightbeam.sporeandstem.fabric;

import com.nightbeam.sporeandstem.client.ModClient;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.blockrenderlayer.v1.BlockRenderLayerMap;
import net.fabricmc.fabric.api.client.particle.v1.ParticleFactoryRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityModelLayerRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.renderer.RenderType;

public class SporeAndStemFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        ModBlocks.CUTOUT.forEach(block -> BlockRenderLayerMap.INSTANCE.putBlock(block.get(), RenderType.cutout()));
        ModClient.registerParticles((type, provider) -> ParticleFactoryRegistry.getInstance().register(type, provider::apply));
        ModClient.registerLayers((layer, definition) -> EntityModelLayerRegistry.registerModelLayer(layer, definition::get));
        ModClient.registerRenderers(EntityRendererRegistry::register);
    }
}
