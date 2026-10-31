package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.entity.projectile.SporeBombEntity;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Thrown like a snowball; bursts into a cloud of Mycosis spores. */
public class SporeBombItem extends Item {

    public SporeBombItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.SPORE_BOMB_THROW.get(),
                SoundSource.PLAYERS, 0.6F, 0.8F + level.random.nextFloat() * 0.3F);
        if (!level.isClientSide) {
            SporeBombEntity bomb = new SporeBombEntity(level, player);
            bomb.setItem(stack);
            bomb.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 1.1F, 1.0F);
            level.addFreshEntity(bomb);
        }
        player.awardStat(Stats.ITEM_USED.get(this));
        player.getCooldowns().addCooldown(this, 10);
        stack.consume(1, player);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }
}
