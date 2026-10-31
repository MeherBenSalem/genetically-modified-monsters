package com.nightbeam.sporeandstem.forge;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.dev.RegistryDump;
import com.nightbeam.sporeandstem.forge.platform.ForgeRegistrar;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModCompostables;
import com.nightbeam.sporeandstem.registry.ModEntities;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ComposterBlock;
import net.minecraft.world.level.block.FlowerPotBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.ToolActions;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;

import java.util.HashMap;
import java.util.Map;

/**
 * Forge entry point. Worldgen and spawns are data on Forge (biome modifiers in the generated resources); everything
 * else is wired here.
 */
@Mod(SporeAndStem.MOD_ID)
public class SporeAndStemForge {
    private static Map<Block, Block> strippables;

    public SporeAndStemForge() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        SporeAndStem.init();
        ForgeRegistrar.registerAll(modBus);
        modBus.addListener(SporeAndStemForge::onAttributes);
        modBus.addListener(SporeAndStemForge::onSpawnPlacements);
        modBus.addListener(SporeAndStemForge::onCommonSetup);
        MinecraftForge.EVENT_BUS.addListener(SporeAndStemForge::onToolModification);
        if (FMLEnvironment.dist.isClient()) {
            SporeAndStemForgeClient.init(modBus);
        }
    }

    private static void onAttributes(EntityAttributeCreationEvent event) {
        ModEntities.registerAttributes((type, builder) -> event.put(type, builder.build()));
    }

    private static void onSpawnPlacements(SpawnPlacementRegisterEvent event) {
        ModEntities.registerSpawnPlacements(new ModEntities.SpawnPlacementSink() {
            @Override
            public <T extends Mob> void register(EntityType<T> type, SpawnPlacements.Type placement, Heightmap.Types heightmap,
                                                 SpawnPlacements.SpawnPredicate<T> predicate) {
                event.register(type, placement, heightmap, predicate, SpawnPlacementRegisterEvent.Operation.REPLACE);
            }
        });
    }

    private static void onCommonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            FlowerPotBlock emptyPot = (FlowerPotBlock) Blocks.FLOWER_POT;
            ModBlocks.POTTED.forEach((pot, plant) -> emptyPot.addPlant(plant.id(), pot::get));
            ModCompostables.forEach((item, chance) -> ComposterBlock.COMPOSTABLES.put(item.asItem(), chance.floatValue()));
        });
        RegistryDump.writeIfDevelopment();
    }

    private static void onToolModification(BlockEvent.BlockToolModificationEvent event) {
        if (event.getToolAction() != ToolActions.AXE_STRIP) {
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
