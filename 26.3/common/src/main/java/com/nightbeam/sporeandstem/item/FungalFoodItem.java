package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.registry.ModEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * A dish or drink. Since 1.21.2 the eating or drinking animation, the sound, the effects and the container left behind
 * all come from the item's consumable component (see ModFoods.Food); this class only adds the Mycosis cure.
 */
public class FungalFoodItem extends Item {
    private final boolean curesMycosis;

    public FungalFoodItem(Properties properties, boolean drink, boolean curesMycosis) {
        super(properties);
        this.curesMycosis = curesMycosis;
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (curesMycosis && !level.isClientSide()) {
            entity.removeEffect(ModEffects.MYCOSIS.holder());
        }
        return super.finishUsingItem(stack, level, entity);
    }
}
