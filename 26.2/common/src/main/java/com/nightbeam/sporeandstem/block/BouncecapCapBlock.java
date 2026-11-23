package com.nightbeam.sporeandstem.block;

import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.HugeMushroomBlock;
import net.minecraft.world.level.block.state.BlockState;

/** A Bouncecap's cap: springy like a slime block, with no fall damage and its own boing. */
public class BouncecapCapBlock extends HugeMushroomBlock {

    public BouncecapCapBlock(Properties properties) {
        // 26.2 bounces through the block's restitution (non-living entities keep 80% of it, as before).
        super(properties.bounceRestitution(0.92F));
    }

    @Override
    public void fallOn(Level level, BlockState state, BlockPos pos, Entity entity, double fallDistance) {
        if (entity.isSuppressingBounce()) {
            super.fallOn(level, state, pos, entity, fallDistance);
        } else {
            entity.causeFallDamage(fallDistance, 0.0F, level.damageSources().fall());
            if (fallDistance > 1.0F && !level.isClientSide()) {
                float pitch = 0.9F + level.getRandom().nextFloat() * 0.3F;
                level.playSound(null, pos, ModSounds.BOUNCECAP_BOUNCE.get(), SoundSource.BLOCKS, 0.8F, pitch);
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
