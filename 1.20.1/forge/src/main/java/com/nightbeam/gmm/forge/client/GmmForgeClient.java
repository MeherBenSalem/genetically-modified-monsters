package com.nightbeam.gmm.forge.client;

import com.nightbeam.gmm.Gmm;
import com.nightbeam.gmm.client.MutantCreeperRenderer;
import com.nightbeam.gmm.registry.ModEntities;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = Gmm.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class GmmForgeClient {
    @SubscribeEvent
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
