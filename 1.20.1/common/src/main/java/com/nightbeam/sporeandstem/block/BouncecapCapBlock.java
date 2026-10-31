package com.nightbeam.sporeandstem.block;

import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.HugeMushroomBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/** A Bouncecap's cap: springy like a slime block, with no fall damage and its own boing. */
public class BouncecapCapBlock extends HugeMushroomBlock {

    public BouncecapCapBlock(Properties properties) {
        super(properties);
    }

    @Override
    public void fallOn(Level level, BlockState state, BlockPos pos, Entity entity, float fallDistance) {
        if (entity.isSuppressingBounce()) {
            super.fallOn(level, state, pos, entity, fallDistance);
        } else {
            entity.causeFallDamage(fallDistance, 0.0F, level.damageSources().fall());
            if (fallDistance > 1.0F && !level.isClientSide) {
                float pitch = 0.9F + level.random.nextFloat() * 0.3F;
                level.playSound(null, pos, ModSounds.BOUNCECAP_BOUNCE.get(), SoundSource.BLOCKS, 0.8F, pitch);
            }
        }
    }

    @Override
    public void updateEntityAfterFallOn(BlockGetter level, Entity entity) {
        if (entity.isSuppressingBounce()) {
            super.updateEntityAfterFallOn(level, entity);
        } else {
            Vec3 motion = entity.getDeltaMovement();
            if (motion.y < 0.0) {
                double factor = entity instanceof LivingEntity ? 1.0 : 0.8;
                entity.setDeltaMovement(motion.x, -motion.y * 0.92 * factor, motion.z);
            }
        }
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        double vy = Math.abs(entity.getDeltaMovement().y);
        if (vy < 0.1 && !entity.isSteppingCarefully()) {
            double slow = 0.4 + vy * 0.2;
            entity.setDeltaMovement(entity.getDeltaMovement().multiply(slow, 1.0, slow));
        }
        super.stepOn(level, pos, state, entity);
    }
}
