package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.platform.Services;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodProperties;

import java.util.function.Supplier;

/**
 * Food values (docs/DESIGN.md §1.2 and §2.2). Effect durations are in ticks. Suppliers, because some foods carry
 * this mod's effects, which Forge only binds once registration runs. Bowls and bottles are handed back by
 * {@link com.nightbeam.sporeandstem.item.FungalFoodItem}, since 1.20.1 food has no remainder.
 */
public final class ModFoods {
    // Raw fungi
    public static final Supplier<FoodProperties> GLOWCAP = () -> new FoodProperties.Builder().nutrition(1).saturationMod(0.1F)
            .effect(new MobEffectInstance(MobEffects.NIGHT_VISION, 200), 1.0F).build();
    public static final Supplier<FoodProperties> BOUNCECAP = () -> new FoodProperties.Builder().nutrition(1).saturationMod(0.1F)
            .effect(new MobEffectInstance(MobEffects.JUMP, 200), 1.0F).build();
    public static final Supplier<FoodProperties> MOREL = () -> new FoodProperties.Builder().nutrition(2).saturationMod(0.3F).build();
    public static final Supplier<FoodProperties> CHANTERELLE = () -> new FoodProperties.Builder().nutrition(2).saturationMod(0.4F).build();
    public static final Supplier<FoodProperties> DEATHCAP = () -> Services.PLATFORM.modEffect(new FoodProperties.Builder()
            .nutrition(1).saturationMod(0.1F).effect(new MobEffectInstance(MobEffects.POISON, 200, 1), 1.0F),
            () -> new MobEffectInstance(ModEffects.MYCOSIS.get(), 400), 1.0F).build();
    public static final Supplier<FoodProperties> FROSTCAP = () -> new FoodProperties.Builder().nutrition(1).saturationMod(0.1F)
            .effect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 200), 1.0F)
            .effect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100), 1.0F).build();
    public static final Supplier<FoodProperties> EMBERSTOOL = () -> new FoodProperties.Builder().nutrition(1).saturationMod(0.1F)
            .effect(new MobEffectInstance(MobEffects.DIG_SPEED, 200), 1.0F).build();
    public static final Supplier<FoodProperties> PUFFBALL = () -> new FoodProperties.Builder().nutrition(2).saturationMod(0.3F).build();
    public static final Supplier<FoodProperties> TRUFFLE = () -> new FoodProperties.Builder().nutrition(3).saturationMod(0.6F)
            .effect(new MobEffectInstance(MobEffects.REGENERATION, 100), 1.0F).build();

    // Dishes
    public static final Supplier<FoodProperties> ROASTED_MOREL = () -> new FoodProperties.Builder().nutrition(6).saturationMod(0.6F).build();
    public static final Supplier<FoodProperties> CHANTERELLE_TOAST = () -> new FoodProperties.Builder().nutrition(8).saturationMod(0.8F).build();
    public static final Supplier<FoodProperties> GLOWCAP_SOUP = () -> new FoodProperties.Builder().nutrition(6).saturationMod(0.6F)
            .effect(new MobEffectInstance(MobEffects.NIGHT_VISION, 1800), 1.0F).build();
    public static final Supplier<FoodProperties> BOUNCECAP_JELLY = () -> new FoodProperties.Builder().nutrition(4).saturationMod(0.4F)
            .effect(new MobEffectInstance(MobEffects.JUMP, 900, 1), 1.0F)
            .effect(new MobEffectInstance(MobEffects.SLOW_FALLING, 300), 1.0F).build();
    public static final Supplier<FoodProperties> FROSTCAP_TEA = () -> new FoodProperties.Builder().nutrition(2).saturationMod(0.2F)
            .alwaysEat().effect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 1800), 1.0F).build();
    public static final Supplier<FoodProperties> EMBER_SKEWER = () -> new FoodProperties.Builder().nutrition(6).saturationMod(0.7F)
            .effect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 600), 1.0F).build();
    public static final Supplier<FoodProperties> TRUFFLE_STEW = () -> new FoodProperties.Builder().nutrition(10).saturationMod(1.2F)
            .effect(new MobEffectInstance(MobEffects.REGENERATION, 160, 1), 1.0F)
            .effect(new MobEffectInstance(MobEffects.ABSORPTION, 1200), 1.0F).build();
    public static final Supplier<FoodProperties> FORAGERS_STEW = () -> new FoodProperties.Builder().nutrition(8).saturationMod(0.8F).build();
    public static final Supplier<FoodProperties> ANTIFUNGAL_TONIC = () -> Services.PLATFORM.modEffect(new FoodProperties.Builder()
            .nutrition(0).saturationMod(0.0F).alwaysEat(),
            () -> new MobEffectInstance(ModEffects.SPORE_WARD.get(), 3600), 1.0F).build();

    private ModFoods() {
    }
}
