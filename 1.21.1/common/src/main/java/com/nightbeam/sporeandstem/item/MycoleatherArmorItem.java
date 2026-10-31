package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.registry.ModArmorMaterials;
import com.nightbeam.sporeandstem.registry.ModEffects;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/** Grown, not tanned. A full set wards off spores (Spore Ward). */
public class MycoleatherArmorItem extends ArmorItem {

    public MycoleatherArmorItem(Type type, Properties properties) {
        super(ModArmorMaterials.MYCOLEATHER.holder(), type, properties);
    }

    public static boolean wearsFullSet(LivingEntity entity) {
        for (EquipmentSlot slot : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
            if (!(entity.getItemBySlot(slot).getItem() instanceof MycoleatherArmorItem)) {
                return false;
            }
        }
        return true;
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        // Only the tunic applies the set bonus, so it is applied once.
        if (!level.isClientSide && this.getType() == Type.CHESTPLATE && entity instanceof LivingEntity living
                && living.getItemBySlot(EquipmentSlot.CHEST) == stack && entity.tickCount % 20 == 0 && wearsFullSet(living)) {
            living.addEffect(new MobEffectInstance(ModEffects.SPORE_WARD.holder(), 60, 0, true, false, true));
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.spore_and_stem.mycoleather_armor.desc").withStyle(ChatFormatting.GRAY));
    }
}
