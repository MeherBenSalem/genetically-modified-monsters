package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.platform.Services;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public final class ModArmorMaterials {
    public static final RegistryEntry<ArmorMaterial> MYCOLEATHER = Services.REGISTRAR.register(Registries.ARMOR_MATERIAL,
            "mycoleather", () -> new ArmorMaterial(defense(2, 5, 4, 2), 18, SoundEvents.ARMOR_EQUIP_LEATHER,
                    () -> Ingredient.of(ModItems.MYCOLEATHER.get()),
                    List.of(new ArmorMaterial.Layer(SporeAndStem.id("mycoleather"))), 0.0F, 0.0F));
    public static final RegistryEntry<ArmorMaterial> BLOOM = Services.REGISTRAR.register(Registries.ARMOR_MATERIAL,
            "bloom", () -> new ArmorMaterial(defense(3, 3, 3, 3), 22, SoundEvents.ARMOR_EQUIP_GOLD,
                    () -> Ingredient.of(ModItems.LUMEN_SPORES.get()),
                    List.of(new ArmorMaterial.Layer(SporeAndStem.id("bloom"))), 2.0F, 0.0F));

    private ModArmorMaterials() {
    }

    private static Map<ArmorItem.Type, Integer> defense(int helmet, int chest, int legs, int boots) {
        Map<ArmorItem.Type, Integer> map = new EnumMap<>(ArmorItem.Type.class);
        map.put(ArmorItem.Type.HELMET, helmet);
        map.put(ArmorItem.Type.CHESTPLATE, chest);
        map.put(ArmorItem.Type.LEGGINGS, legs);
        map.put(ArmorItem.Type.BOOTS, boots);
        map.put(ArmorItem.Type.BODY, chest);
        return map;
    }

    public static void init() {
    }
}
