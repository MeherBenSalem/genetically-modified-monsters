package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.entity.MyceliarchEntity;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;

import java.util.List;

/** Used on Mycelium, Mycelial Soil, Podzol or Moss, it calls up the Myceliarch. */
public class FruitingHeartItem extends Item {

    public FruitingHeartItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        if (!context.getLevel().getBlockState(context.getClickedPos()).is(ModTags.Blocks.MYCELIARCH_SUMMON_BLOCKS)) {
            return InteractionResult.PASS;
        }
        if (context.getLevel() instanceof ServerLevel level) {
            if (!MyceliarchEntity.summon(level, context.getClickedPos().above(), context.getPlayer())) {
                return InteractionResult.FAIL;
            }
            context.getItemInHand().consume(1, context.getPlayer());
        }
        return InteractionResult.sidedSuccess(context.getLevel().isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.spore_and_stem.fruiting_heart.desc").withStyle(ChatFormatting.GRAY));
    }
}
