package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.effect.MycosisEffect;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModItems;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.tags.TagKey;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * The Myceliarch's blade. Hits infect (Mycosis II, 6 s). Use: Spore Burst, a ring of spores that infects, slows and
 * shoves back everything around you (10 s cooldown, 3 durability).
 */
public class BloomreaverItem extends SwordItem {
    public static final Tier TIER = new Tier() {
        @Override
        public int getUses() {
            return 1800;
        }

        @Override
        public float getSpeed() {
            return 8.0F;
        }

        @Override
        public float getAttackDamageBonus() {
            return 3.0F;
        }

        @Override
        public TagKey<Block> getIncorrectBlocksForDrops() {
            return BlockTags.INCORRECT_FOR_DIAMOND_TOOL;
        }

        @Override
        public int getEnchantmentValue() {
            return 15;
        }

        @Override
        public Ingredient getRepairIngredient() {
            return Ingredient.of(ModItems.LUMEN_SPORES.get());
        }
    };
    public static final int COOLDOWN = 200;
    public static final double RADIUS = 4.0;

    public BloomreaverItem(Properties properties) {
        // 1 base + 3 tier bonus + 4 = 8 attack damage.
        super(TIER, properties.attributes(SwordItem.createAttributes(TIER, 4, -2.4F)));
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        if (!MycosisEffect.isImmune(target)) {
            target.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 120, 1), attacker);
        }
        return super.hurtEnemy(stack, target, attacker);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level instanceof ServerLevel server) {
            sporeBurst(server, player);
            stack.hurtAndBreak(3, player, hand == InteractionHand.MAIN_HAND ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);
        }
        player.getCooldowns().addCooldown(this, COOLDOWN);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    public static void sporeBurst(ServerLevel level, LivingEntity source) {
        level.playSound(null, source.getX(), source.getY(), source.getZ(), ModSounds.BLOOMREAVER_BURST.get(),
                SoundSource.PLAYERS, 1.0F, 0.9F + level.random.nextFloat() * 0.2F);
        for (int i = 0; i < 48; i++) {
            double angle = i * Math.PI * 2 / 48;
            double x = source.getX() + Math.cos(angle) * 1.2;
            double z = source.getZ() + Math.sin(angle) * 1.2;
            level.sendParticles(ModParticles.SPORE.get(), x, source.getY() + 0.6, z, 0, Math.cos(angle), 0.05,
                    Math.sin(angle), 0.35);
        }
        level.sendParticles(ModParticles.GLOW_SPORE.get(), source.getX(), source.getY() + 1.0, source.getZ(), 30, 1.5, 0.6, 1.5, 0.02);
        for (LivingEntity other : level.getEntitiesOfClass(LivingEntity.class, source.getBoundingBox().inflate(RADIUS),
                e -> e != source && e.isAlive() && e.distanceToSqr(source) <= RADIUS * RADIUS && !source.isAlliedTo(e))) {
            if (!MycosisEffect.isImmune(other)) {
                other.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 160, 1), source);
            }
            other.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 120, 1), source);
            Vec3 push = other.position().subtract(source.position()).multiply(1, 0, 1).normalize().scale(0.9);
            other.push(push.x, 0.35, push.z);
            other.hurtMarked = true;
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.spore_and_stem.bloomreaver.desc").withStyle(ChatFormatting.GRAY));
    }
}
