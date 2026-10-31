package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.registry.ModEffects;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

/** A dish or drink. Drinks use the drinking animation; some cure Mycosis. The bowl, bottle or stick comes back. */
public class FungalFoodItem extends Item {
    private final boolean drink;
    private final boolean curesMycosis;
    @Nullable
    private final Item remainder;

    public FungalFoodItem(Properties properties, boolean drink, boolean curesMycosis, @Nullable Item remainder) {
        super(properties);
        this.drink = drink;
        this.curesMycosis = curesMycosis;
        this.remainder = remainder;
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (curesMycosis && !level.isClientSide) {
            entity.removeEffect(ModEffects.MYCOSIS.get());
        }
        ItemStack result = super.finishUsingItem(stack, level, entity);
        if (remainder == null || entity instanceof Player player && player.getAbilities().instabuild) {
            return result;
        }
        if (result.isEmpty()) {
            return new ItemStack(remainder);
        }
        if (entity instanceof Player player && !level.isClientSide) {
            ItemStack container = new ItemStack(remainder);
            if (!player.getInventory().add(container)) {
                player.drop(container, false);
            }
        }
        return result;
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
