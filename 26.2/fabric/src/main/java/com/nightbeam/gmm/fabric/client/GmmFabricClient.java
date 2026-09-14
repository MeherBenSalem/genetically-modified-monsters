package com.nightbeam.gmm.fabric.client;

import com.nightbeam.gmm.client.MutantCreeperRenderer;
import com.nightbeam.gmm.registry.ModEntities;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

public class GmmFabricClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        EntityRendererRegistry.register(ModEntities.LEAP_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "leap_creeper"));
        EntityRendererRegistry.register(ModEntities.CLIMB_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "climb_creeper"));
        EntityRendererRegistry.register(ModEntities.SWIFT_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "swift_creeper"));
        EntityRendererRegistry.register(ModEntities.ADAPTIVE_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "adaptive_creeper"));
        EntityRendererRegistry.register(ModEntities.OVERCHARGE_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "overcharge_creeper"));
        EntityRendererRegistry.register(ModEntities.SILENT_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "silent_creeper"));
        EntityRendererRegistry.register(ModEntities.HUNTER_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "hunter_creeper"));
    }
}
