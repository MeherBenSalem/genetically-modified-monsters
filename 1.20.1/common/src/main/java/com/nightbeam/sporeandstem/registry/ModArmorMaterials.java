package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.SporeAndStem;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.function.Supplier;

/**
 * Armor materials. In 1.20.1 these are plain constants, not a registry. The namespaced name makes both loaders read
 * the layers from {@code spore_and_stem:textures/models/armor/<name>_layer_N.png}.
 */
public enum ModArmorMaterials implements ArmorMaterial {
    // Durability multiplier 14 (between leather 5 and iron 15), defense 2/5/4/2.
    MYCOLEATHER("mycoleather", 14, new int[]{2, 5, 4, 2}, 18, SoundEvents.ARMOR_EQUIP_LEATHER, 0.0F,
            () -> Ingredient.of(ModItems.MYCOLEATHER.get())),
    // The Crown of the Bloom sets its own durability (600); defense 3, toughness 2.
    BLOOM("bloom", 0, new int[]{3, 3, 3, 3}, 22, SoundEvents.ARMOR_EQUIP_GOLD, 2.0F,
            () -> Ingredient.of(ModItems.LUMEN_SPORES.get()));

    /** Vanilla's per-slot durability base (helmet, chestplate, leggings, boots). */
    private static final int[] DURABILITY_BASE = {11, 16, 15, 13};

    private final String name;
    private final int durabilityMultiplier;
    private final int[] defense;
    private final int enchantability;
    private final SoundEvent equipSound;
    private final float toughness;
    private final Supplier<Ingredient> repair;

    ModArmorMaterials(String name, int durabilityMultiplier, int[] defense, int enchantability, SoundEvent equipSound,
                      float toughness, Supplier<Ingredient> repair) {
        this.name = name;
        this.durabilityMultiplier = durabilityMultiplier;
        this.defense = defense;
        this.enchantability = enchantability;
        this.equipSound = equipSound;
        this.toughness = toughness;
        this.repair = repair;
    }

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return DURABILITY_BASE[type.ordinal()] * durabilityMultiplier;
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return defense[type.ordinal()];
    }

    @Override
    public int getEnchantmentValue() {
        return enchantability;
    }

    @Override
    public SoundEvent getEquipSound() {
        return equipSound;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return repair.get();
    }

    @Override
    public String getName() {
        return SporeAndStem.MOD_ID + ":" + name;
    }

    @Override
    public float getToughness() {
        return toughness;
    }

    @Override
    public float getKnockbackResistance() {
        return 0.0F;
    }

    public static void init() {
    }
}
