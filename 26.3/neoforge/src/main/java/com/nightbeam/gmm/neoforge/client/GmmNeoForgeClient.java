package com.nightbeam.gmm.neoforge.client;

import com.nightbeam.gmm.client.MutantCreeperRenderer;
import com.nightbeam.gmm.registry.ModEntities;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

public final class GmmNeoForgeClient {
    private GmmNeoForgeClient() {
    }

    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.LEAP_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "leap_creeper"));
        event.registerEntityRenderer(ModEntities.CLIMB_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "climb_creeper"));
        event.registerEntityRenderer(ModEntities.SWIFT_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "swift_creeper"));
        event.registerEntityRenderer(ModEntities.ADAPTIVE_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "adaptive_creeper"));
        event.registerEntityRenderer(ModEntities.OVERCHARGE_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "overcharge_creeper"));
        event.registerEntityRenderer(ModEntities.SILENT_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "silent_creeper"));
        event.registerEntityRenderer(ModEntities.HUNTER_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "hunter_creeper"));
    }
}
