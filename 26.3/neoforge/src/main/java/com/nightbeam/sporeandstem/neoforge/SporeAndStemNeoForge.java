package com.nightbeam.sporeandstem.neoforge;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.block.FungusStripping;
import com.nightbeam.sporeandstem.dev.RegistryDump;
import com.nightbeam.sporeandstem.neoforge.gametest.SporeAndStemNeoForgeGameTests;
import com.nightbeam.sporeandstem.neoforge.platform.NeoForgeRegistrar;
import com.nightbeam.sporeandstem.registry.ModEntities;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.SpawnPlacementType;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;


/**
 * NeoForge entry point. Worldgen and spawns are data on NeoForge (biome modifiers in the generated resources); compost
 * chances are the items' compostable component on 26.3 (ModCompostables); everything else is wired here.
 */
@Mod(SporeAndStem.MOD_ID)
public class SporeAndStemNeoForge {
    public SporeAndStemNeoForge(IEventBus modBus) {
        SporeAndStem.init();
        NeoForgeRegistrar.registerAll(modBus);
        SporeAndStemNeoForgeGameTests.register(modBus);
        modBus.addListener(SporeAndStemNeoForge::onAttributes);
        modBus.addListener(SporeAndStemNeoForge::onSpawnPlacements);
        modBus.addListener(SporeAndStemNeoForge::onCommonSetup);
        NeoForge.EVENT_BUS.addListener(SporeAndStemNeoForge::onRightClickBlock);
        if (FMLEnvironment.getDist().isClient()) {
            SporeAndStemNeoForgeClient.init(modBus);
        }
    }

    private static void onAttributes(EntityAttributeCreationEvent event) {
        ModEntities.registerAttributes((type, builder) -> event.put(type, builder.build()));
    }

    private static void onSpawnPlacements(RegisterSpawnPlacementsEvent event) {
        ModEntities.registerSpawnPlacements(new ModEntities.SpawnPlacementSink() {
            @Override
            public <T extends Mob> void register(EntityType<T> type, SpawnPlacementType placement, Heightmap.Types heightmap,
                                                 SpawnPlacements.SpawnPredicate<T> predicate) {
                event.register(type, placement, heightmap, predicate, RegisterSpawnPlacementsEvent.Operation.REPLACE);
            }
        });
    }

    private static void onCommonSetup(FMLCommonSetupEvent event) {
        // 26.3: NeoForge files every FlowerPotBlock under its empty pot when it registers, so the potted fungi
        // need no addPlant call any more.
        RegistryDump.writeIfDevelopment();
    }

    private static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        // 26.3: stripping is the axe's block transformer; NeoForge's AXE_STRIP tool modification is gone.
        InteractionResult result = FungusStripping.onUseBlock(event.getEntity(), event.getLevel(), event.getHand(), event.getHitVec());
        if (result != InteractionResult.PASS) {
            event.setCanceled(true);
            event.setCancellationResult(result);
        }
    }
}
