package com.nightbeam.sporeandstem.registry;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.Consumable;
import net.minecraft.world.item.component.Consumables;
import net.minecraft.world.item.consume_effects.ApplyStatusEffectsConsumeEffect;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.function.Supplier;

/**
 * Food values (docs/DESIGN.md §1.2 and §2.2). Effect durations are in ticks. Since 1.21.2 the nutrition lives in the
 * food component and the effects, eating or drinking animation and the container left behind in the consumable
 * component; {@link Food} builds both. Effects are suppliers, because some foods carry this mod's effects, which
 * NeoForge only binds once registration runs.
 */
public final class ModFoods {
    // Raw fungi
    public static final Food GLOWCAP = food(1, 0.1F, () -> List.of(new MobEffectInstance(MobEffects.NIGHT_VISION, 200)));
    public static final Food BOUNCECAP = food(1, 0.1F, () -> List.of(new MobEffectInstance(MobEffects.JUMP_BOOST, 200)));
    public static final Food MOREL = food(2, 0.3F, List::of);
    public static final Food CHANTERELLE = food(2, 0.4F, List::of);
    public static final Food DEATHCAP = food(1, 0.1F, () -> List.of(new MobEffectInstance(MobEffects.POISON, 200, 1),
            new MobEffectInstance(ModEffects.MYCOSIS.holder(), 400)));
    public static final Food FROSTCAP = food(1, 0.1F, () -> List.of(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 200),
            new MobEffectInstance(MobEffects.SLOWNESS, 100)));
    public static final Food EMBERSTOOL = food(1, 0.1F, () -> List.of(new MobEffectInstance(MobEffects.HASTE, 200)));
    public static final Food PUFFBALL = food(2, 0.3F, List::of);
    public static final Food TRUFFLE = food(3, 0.6F, () -> List.of(new MobEffectInstance(MobEffects.REGENERATION, 100)));

    // Dishes
    public static final Food ROASTED_MOREL = food(6, 0.6F, List::of);
    public static final Food CHANTERELLE_TOAST = food(8, 0.8F, List::of);
    public static final Food GLOWCAP_SOUP = food(6, 0.6F, () -> List.of(new MobEffectInstance(MobEffects.NIGHT_VISION, 1800)))
            .leaving(Items.BOWL);
    public static final Food BOUNCECAP_JELLY = food(4, 0.4F, () -> List.of(new MobEffectInstance(MobEffects.JUMP_BOOST, 900, 1),
            new MobEffectInstance(MobEffects.SLOW_FALLING, 300))).leaving(Items.GLASS_BOTTLE);
    public static final Food FROSTCAP_TEA = food(2, 0.2F, () -> List.of(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 1800)))
            .always().leaving(Items.GLASS_BOTTLE);
    public static final Food EMBER_SKEWER = food(6, 0.7F, () -> List.of(new MobEffectInstance(MobEffects.STRENGTH, 600)))
            .leaving(Items.STICK);
    public static final Food TRUFFLE_STEW = food(10, 1.2F, () -> List.of(new MobEffectInstance(MobEffects.REGENERATION, 160, 1),
            new MobEffectInstance(MobEffects.ABSORPTION, 1200))).leaving(Items.BOWL);
    public static final Food FORAGERS_STEW = food(8, 0.8F, List::of).leaving(Items.BOWL);
    public static final Food ANTIFUNGAL_TONIC = food(0, 0.0F, () -> List.of(new MobEffectInstance(ModEffects.SPORE_WARD.holder(), 3600)))
            .always().leaving(Items.GLASS_BOTTLE);

    private ModFoods() {
    }

    private static Food food(int nutrition, float saturation, Supplier<List<MobEffectInstance>> effects) {
        return new Food(nutrition, saturation, false, null, effects);
    }

    /** One food: its nutrition, whether it can be eaten when full, the container it leaves and its effects. */
    public record Food(int nutrition, float saturation, boolean alwaysEdible, @Nullable Item remainder,
                       Supplier<List<MobEffectInstance>> effects) {

        Food always() {
            return new Food(nutrition, saturation, true, remainder, effects);
        }

        Food leaving(Item container) {
            return new Food(nutrition, saturation, alwaysEdible, container, effects);
        }

        public FoodProperties get() {
            FoodProperties.Builder builder = new FoodProperties.Builder().nutrition(nutrition).saturationModifier(saturation);
            if (alwaysEdible) {
                builder.alwaysEdible();
            }
            return builder.build();
        }

        /** Eaten: the eating animation and sound, then the effects. */
        public Supplier<Consumable> eat() {
            return () -> withEffects(Consumables.defaultFood());
        }

        /** Drunk: the drinking animation and sound, then the effects. */
        public Supplier<Consumable> drink() {
            return () -> withEffects(Consumables.defaultDrink());
        }

        private Consumable withEffects(Consumable.Builder builder) {
            List<MobEffectInstance> list = effects.get();
            if (!list.isEmpty()) {
                builder.onConsume(new ApplyStatusEffectsConsumeEffect(list));
            }
            return builder.build();
        }
    }
}
