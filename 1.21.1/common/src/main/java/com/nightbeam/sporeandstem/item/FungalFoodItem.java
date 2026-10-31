package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.registry.ModEffects;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

/** A dish or drink. Drinks use the drinking animation; some cure Mycosis. Containers come back via the food. */
public class FungalFoodItem extends Item {
    private final boolean drink;
    private final boolean curesMycosis;

    public FungalFoodItem(Properties properties, boolean drink, boolean curesMycosis) {
        super(properties);
        this.drink = drink;
        this.curesMycosis = curesMycosis;
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (curesMycosis && !level.isClientSide) {
            entity.removeEffect(ModEffects.MYCOSIS.holder());
        }
        return super.finishUsingItem(stack, level, entity);
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return drink ? UseAnim.DRINK : UseAnim.EAT;
    }

    @Override
    public SoundEvent getDrinkingSound() {
        return SoundEvents.HONEY_DRINK;
    }

    @Override
    public SoundEvent getEatingSound() {
        return drink ? SoundEvents.HONEY_DRINK : super.getEatingSound();
    }
}
