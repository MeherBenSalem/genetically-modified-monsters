package com.nightbeam.sporeandstem.registry;

import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.providers.number.ints.ContextIntProviders;

import java.util.Map;

/**
 * Composting chances. Since Minecraft 26.3 the chance is the item's own compostable component, so every item built
 * through {@link Keys#itemProps()} gets it here by name (the composter's chance table is gone). Chances map onto
 * vanilla's tiers: 0.3 low, 0.5 low-medium, 0.65 medium, 0.85 medium-high.
 */
public final class ModCompostables {
    private static final Map<String, Float> CHANCES = Map.ofEntries(
            Map.entry("glowcap", 0.65F), Map.entry("bouncecap", 0.65F), Map.entry("inkcap", 0.65F),
            Map.entry("morel", 0.65F), Map.entry("chanterelle", 0.65F), Map.entry("deathcap", 0.65F),
            Map.entry("frostcap", 0.65F), Map.entry("emberstool", 0.65F), Map.entry("puffball", 0.65F),
            Map.entry("glowcap_cap", 0.85F), Map.entry("bouncecap_cap", 0.85F), Map.entry("inkcap_cap", 0.85F),
            Map.entry("glowcap_gills", 0.65F), Map.entry("shelf_fungus", 0.65F), Map.entry("mycelial_veil", 0.5F),
            Map.entry("giant_puffball", 0.85F), Map.entry("truffle", 0.65F), Map.entry("lumen_spores", 0.3F));

    private ModCompostables() {
    }

    public static Map<String, Float> chances() {
        return CHANCES;
    }

    /** Adds the compostable component to the properties of item {@code name}, if it composts. */
    public static Item.Properties apply(Item.Properties properties, String name) {
        Float chance = CHANCES.get(name);
        if (chance == null) {
            return properties;
        }
        if (chance <= 0.3F) {
            return properties.compostable(ContextIntProviders.COMPOSTABLE_LOW);
        }
        if (chance <= 0.5F) {
            return properties.compostable(ContextIntProviders.COMPOSTABLE_LOW_MEDIUM);
        }
        if (chance <= 0.65F) {
            return properties.compostable(ContextIntProviders.COMPOSTABLE_MEDIUM);
        }
        return properties.compostable(ContextIntProviders.COMPOSTABLE_MEDIUM_HIGH);
    }
}
