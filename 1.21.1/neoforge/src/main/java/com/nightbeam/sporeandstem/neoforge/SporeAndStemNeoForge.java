package com.nightbeam.sporeandstem.neoforge;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.dev.RegistryDump;
import com.nightbeam.sporeandstem.neoforge.platform.NeoForgeRegistrar;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModEntities;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.SpawnPlacementType;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FlowerPotBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.ItemAbilities;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.event.level.BlockEvent;

import java.util.HashMap;
import java.util.Map;

/**
 * NeoForge entry point. Worldgen, spawns and compostables are data on NeoForge (biome modifiers and data maps in the
 * generated resources); everything else is wired here.
 */
@Mod(SporeAndStem.MOD_ID)
public class SporeAndStemNeoForge {
    private static Map<Block, Block> strippables;

    public SporeAndStemNeoForge(IEventBus modBus) {
        SporeAndStem.init();
        NeoForgeRegistrar.registerAll(modBus);
        modBus.addListener(SporeAndStemNeoForge::onAttributes);
        modBus.addListener(SporeAndStemNeoForge::onSpawnPlacements);
        modBus.addListener(SporeAndStemNeoForge::onCommonSetup);
        NeoForge.EVENT_BUS.addListener(SporeAndStemNeoForge::onToolModification);
        if (FMLEnvironment.dist.isClient()) {
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
        event.enqueueWork(() -> {
            FlowerPotBlock emptyPot = (FlowerPotBlock) Blocks.FLOWER_POT;
            ModBlocks.POTTED.forEach((pot, plant) -> emptyPot.addPlant(plant.id(), pot::get));
        });
        RegistryDump.writeIfDevelopment();
    }

    private static void onToolModification(BlockEvent.BlockToolModificationEvent event) {
        if (event.getItemAbility() != ItemAbilities.AXE_STRIP) {
            return;
        }
        if (strippables == null) {
            Map<Block, Block> map = new HashMap<>();
            ModBlocks.STRIPPABLES.forEach((log, stripped) -> map.put(log.get(), stripped.get()));
            strippables = map;
        }
        BlockState state = event.getState();
        Block stripped = strippables.get(state.getBlock());
        if (stripped != null) {
            event.setFinalState(stripped.withPropertiesOf(state));
        }
    }
}
