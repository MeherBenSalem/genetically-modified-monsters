package com.nightbeam.gmm.entity.ai;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

public class HazardAvoidGoal extends Goal {
    private final Creeper creeper;
    private Vec3 flee;

    public HazardAvoidGoal(Creeper creeper) {
        this.creeper = creeper;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        BlockPos pos = creeper.blockPosition();
        for (BlockPos check : BlockPos.betweenClosed(pos.offset(-2, -1, -2), pos.offset(2, 1, 2))) {
            BlockState state = creeper.level().getBlockState(check);
            if (state.is(Blocks.LAVA) || state.is(Blocks.FIRE) || state.is(Blocks.SOUL_FIRE)
                    || state.is(Blocks.MAGMA_BLOCK) || state.is(Blocks.CACTUS) || state.is(BlockTags.CAMPFIRES)) {
                flee = creeper.position().subtract(Vec3.atCenterOf(check)).normalize().scale(1.1D);
                return true;
            }
        }
        return false;
    }

    @Override
    public void start() {
        if (flee != null) {
            creeper.getNavigation().stop();
            creeper.setDeltaMovement(creeper.getDeltaMovement().add(flee.x, 0.2D, flee.z));
            creeper.syncVelocity = true;
        }
    }

    @Override
    public boolean canContinueToUse() {
        return false;
    }
}
