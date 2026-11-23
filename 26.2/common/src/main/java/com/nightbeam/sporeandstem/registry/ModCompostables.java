package com.nightbeam.sporeandstem.registry;

import net.minecraft.world.level.ItemLike;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.BiConsumer;

/**
 * Composting chances. Fabric registers these in code; NeoForge reads the same values from the generated
 * {@code neoforge:compostables} data map (tools/assets keeps the two in step).
 */
public final class ModCompostables {

    private ModCompostables() {
    }

    public static Map<ItemLike, Float> all() {
        Map<ItemLike, Float> map = new LinkedHashMap<>();
        for (RegistryEntry<?> fungus : new RegistryEntry<?>[]{ModItems.GLOWCAP, ModItems.BOUNCECAP, ModItems.INKCAP,
                ModItems.MOREL, ModItems.CHANTERELLE, ModItems.DEATHCAP, ModItems.FROSTCAP, ModItems.EMBERSTOOL, ModItems.PUFFBALL}) {
            map.put((ItemLike) fungus.get(), 0.65F);
        }
        map.put(ModBlocks.GLOWCAP_CAP.get(), 0.85F);
        map.put(ModBlocks.BOUNCECAP_CAP.get(), 0.85F);
        map.put(ModBlocks.INKCAP_CAP.get(), 0.85F);
        map.put(ModBlocks.GLOWCAP_GILLS.get(), 0.65F);
        map.put(ModBlocks.SHELF_FUNGUS.get(), 0.65F);
        map.put(ModBlocks.MYCELIAL_VEIL.get(), 0.5F);
        map.put(ModBlocks.GIANT_PUFFBALL.get(), 0.85F);
        map.put(ModItems.TRUFFLE.get(), 0.65F);
        map.put(ModItems.LUMEN_SPORES.get(), 0.3F);
        return map;
    }

    public static void forEach(BiConsumer<ItemLike, Float> sink) {
        all().forEach(sink);
    }
}
