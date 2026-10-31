package com.nightbeam.sporeandstem.registry;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Items;

import java.util.function.Supplier;

/**
 * Food values (docs/DESIGN.md §1.2 and §2.2). Effect durations are in ticks. Suppliers, because some foods carry
 * this mod's effects, which NeoForge only binds once registration runs.
 */
public final class ModFoods {
    // Raw fungi
    public static final Supplier<FoodProperties> GLOWCAP = () -> new FoodProperties.Builder().nutrition(1).saturationModifier(0.1F)
            .effect(new MobEffectInstance(MobEffects.NIGHT_VISION, 200), 1.0F).build();
    public static final Supplier<FoodProperties> BOUNCECAP = () -> new FoodProperties.Builder().nutrition(1).saturationModifier(0.1F)
            .effect(new MobEffectInstance(MobEffects.JUMP, 200), 1.0F).build();
    public static final Supplier<FoodProperties> MOREL = () -> new FoodProperties.Builder().nutrition(2).saturationModifier(0.3F).build();
    public static final Supplier<FoodProperties> CHANTERELLE = () -> new FoodProperties.Builder().nutrition(2).saturationModifier(0.4F).build();
    public static final Supplier<FoodProperties> DEATHCAP = () -> new FoodProperties.Builder().nutrition(1).saturationModifier(0.1F)
            .effect(new MobEffectInstance(MobEffects.POISON, 200, 1), 1.0F)
            .effect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 400), 1.0F).build();
    public static final Supplier<FoodProperties> FROSTCAP = () -> new FoodProperties.Builder().nutrition(1).saturationModifier(0.1F)
            .effect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 200), 1.0F)
            .effect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100), 1.0F).build();
    public static final Supplier<FoodProperties> EMBERSTOOL = () -> new FoodProperties.Builder().nutrition(1).saturationModifier(0.1F)
            .effect(new MobEffectInstance(MobEffects.DIG_SPEED, 200), 1.0F).build();
    public static final Supplier<FoodProperties> PUFFBALL = () -> new FoodProperties.Builder().nutrition(2).saturationModifier(0.3F).build();
    public static final Supplier<FoodProperties> TRUFFLE = () -> new FoodProperties.Builder().nutrition(3).saturationModifier(0.6F)
            .effect(new MobEffectInstance(MobEffects.REGENERATION, 100), 1.0F).build();

    // Dishes
    public static final Supplier<FoodProperties> ROASTED_MOREL = () -> new FoodProperties.Builder().nutrition(6).saturationModifier(0.6F).build();
    public static final Supplier<FoodProperties> CHANTERELLE_TOAST = () -> new FoodProperties.Builder().nutrition(8).saturationModifier(0.8F).build();
    public static final Supplier<FoodProperties> GLOWCAP_SOUP = () -> new FoodProperties.Builder().nutrition(6).saturationModifier(0.6F)
            .effect(new MobEffectInstance(MobEffects.NIGHT_VISION, 1800), 1.0F).usingConvertsTo(Items.BOWL).build();
    public static final Supplier<FoodProperties> BOUNCECAP_JELLY = () -> new FoodProperties.Builder().nutrition(4).saturationModifier(0.4F)
            .effect(new MobEffectInstance(MobEffects.JUMP, 900, 1), 1.0F)
            .effect(new MobEffectInstance(MobEffects.SLOW_FALLING, 300), 1.0F)
            .usingConvertsTo(Items.GLASS_BOTTLE).build();
    public static final Supplier<FoodProperties> FROSTCAP_TEA = () -> new FoodProperties.Builder().nutrition(2).saturationModifier(0.2F)
            .alwaysEdible().effect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 1800), 1.0F)
            .usingConvertsTo(Items.GLASS_BOTTLE).build();
    public static final Supplier<FoodProperties> EMBER_SKEWER = () -> new FoodProperties.Builder().nutrition(6).saturationModifier(0.7F)
            .effect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 600), 1.0F).usingConvertsTo(Items.STICK).build();
    public static final Supplier<FoodProperties> TRUFFLE_STEW = () -> new FoodProperties.Builder().nutrition(10).saturationModifier(1.2F)
            .effect(new MobEffectInstance(MobEffects.REGENERATION, 160, 1), 1.0F)
            .effect(new MobEffectInstance(MobEffects.ABSORPTION, 1200), 1.0F).usingConvertsTo(Items.BOWL).build();
    public static final Supplier<FoodProperties> FORAGERS_STEW = () -> new FoodProperties.Builder().nutrition(8).saturationModifier(0.8F)
            .usingConvertsTo(Items.BOWL).build();
    public static final Supplier<FoodProperties> ANTIFUNGAL_TONIC = () -> new FoodProperties.Builder().nutrition(0).saturationModifier(0.0F)
            .alwaysEdible().effect(new MobEffectInstance(ModEffects.SPORE_WARD.holder(), 3600), 1.0F)
            .usingConvertsTo(Items.GLASS_BOTTLE).build();

    private ModFoods() {
    }
}
