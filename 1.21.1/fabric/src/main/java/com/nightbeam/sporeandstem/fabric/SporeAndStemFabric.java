package com.nightbeam.sporeandstem.fabric;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.dev.RegistryDump;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModCompostables;
import com.nightbeam.sporeandstem.registry.ModEntities;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.fabricmc.fabric.api.registry.CompostingChanceRegistry;
import net.fabricmc.fabric.api.registry.StrippableBlockRegistry;
import net.minecraft.world.entity.SpawnPlacements;

/**
 * Fabric entry point. Worldgen and spawns are added in {@link FabricWorldgen} from the same biome tags the NeoForge
 * biome modifiers use.
 */
public class SporeAndStemFabric implements ModInitializer {

    @Override
    public void onInitialize() {
        SporeAndStem.init();
        ModEntities.registerAttributes(FabricDefaultAttributeRegistry::register);
        ModEntities.registerSpawnPlacements(SpawnPlacements::register);
        ModBlocks.STRIPPABLES.forEach((log, stripped) -> StrippableBlockRegistry.register(log.get(), stripped.get()));
        ModCompostables.forEach((item, chance) -> CompostingChanceRegistry.INSTANCE.add(item, chance));
        FabricWorldgen.init();
        RegistryDump.writeIfDevelopment();
    }
}
