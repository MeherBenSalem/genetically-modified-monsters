package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.registry.ModArmorMaterials;
import com.nightbeam.sporeandstem.registry.ModEffects;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/** The Myceliarch's crown: Night Vision and Spore Ward while worn, and Sporelings trust you. */
public class CrownOfTheBloomItem extends ArmorItem {

    public CrownOfTheBloomItem(Properties properties) {
        super(ModArmorMaterials.BLOOM.holder(), Type.HELMET, properties);
    }

    public static boolean isWorn(LivingEntity entity) {
        return entity.getItemBySlot(EquipmentSlot.HEAD).getItem() instanceof CrownOfTheBloomItem;
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        if (!level.isClientSide && entity instanceof LivingEntity living && living.getItemBySlot(EquipmentSlot.HEAD) == stack
                && entity.tickCount % 20 == 0) {
            living.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 260, 0, true, false, true));
            living.addEffect(new MobEffectInstance(ModEffects.SPORE_WARD.holder(), 60, 0, true, false, true));
        }
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.spore_and_stem.crown_of_the_bloom.desc").withStyle(ChatFormatting.GRAY));
    }
}
