package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.SporeAndStem;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;

import java.util.EnumMap;
import java.util.Map;

/**
 * Armor materials. Since 1.21.2 these are plain records, not registry entries: the worn look comes from the
 * equipment asset ({@code assets/spore_and_stem/equipment/<name>.json}) and repairs from an item tag.
 */
public final class ModArmorMaterials {
    /** Repairs Mycoleather armor (the tag holds Mycoleather). */
    public static final TagKey<Item> MYCOLEATHER_REPAIRS = TagKey.create(Registries.ITEM, SporeAndStem.id("mycoleather_repairs"));
    /** Repairs the Crown of the Bloom and the Bloomreaver (the tag holds Lumen Spores). */
    public static final TagKey<Item> BLOOM_REPAIRS = TagKey.create(Registries.ITEM, SporeAndStem.id("bloom_repairs"));

    // Durability multipliers match the 1.21.1 values: Mycoleather 14 (set per item there), the crown a fixed 600.
    public static final ArmorMaterial MYCOLEATHER = new ArmorMaterial(14, defense(2, 5, 4, 2), 18,
            SoundEvents.ARMOR_EQUIP_LEATHER, 0.0F, 0.0F, MYCOLEATHER_REPAIRS, asset("mycoleather"));
    public static final ArmorMaterial BLOOM = new ArmorMaterial(40, defense(3, 3, 3, 3), 22,
            SoundEvents.ARMOR_EQUIP_GOLD, 2.0F, 0.0F, BLOOM_REPAIRS, asset("bloom"));

    private ModArmorMaterials() {
    }

    private static ResourceKey<EquipmentAsset> asset(String name) {
        return ResourceKey.create(EquipmentAssets.ROOT_ID, SporeAndStem.id(name));
    }

    private static Map<ArmorType, Integer> defense(int helmet, int chest, int legs, int boots) {
        Map<ArmorType, Integer> map = new EnumMap<>(ArmorType.class);
        map.put(ArmorType.HELMET, helmet);
        map.put(ArmorType.CHESTPLATE, chest);
        map.put(ArmorType.LEGGINGS, legs);
        map.put(ArmorType.BOOTS, boots);
        map.put(ArmorType.BODY, chest);
        return map;
    }

    public static void init() {
    }
}
