package com.nightbeam.sporeandstem.entity.ai;

import com.nightbeam.sporeandstem.block.FungusBlock;
import com.nightbeam.sporeandstem.entity.SporelingEntity;
import com.nightbeam.sporeandstem.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.block.MushroomBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.util.EnumSet;

/**
 * Now and then a Sporeling wanders to a small mushroom nearby, fusses over it, and sometimes a new one sprouts beside
 * it (a slow, gentle bone meal: it never grows huge fungi).
 */
public class TendFungiGoal extends Goal {
    private static final int RANGE = 6;
    private final SporelingEntity mob;
    private BlockPos target;
    private int cooldown;
    private int ticks;

    public TendFungiGoal(SporelingEntity mob) {
        this.mob = mob;
        this.cooldown = 200 + mob.getRandom().nextInt(600);
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (mob.isInSittingPose() || mob.isOrderedToSit() || mob.isBaby() || --cooldown > 0) {
            return false;
        }
        cooldown = 600 + mob.getRandom().nextInt(1200);
        BlockPos origin = mob.blockPosition();
        BlockPos best = null;
        double bestDist = Double.MAX_VALUE;
        for (BlockPos pos : BlockPos.betweenClosed(origin.offset(-RANGE, -2, -RANGE), origin.offset(RANGE, 2, RANGE))) {
            if (mob.level().getBlockState(pos).getBlock() instanceof MushroomBlock) {
                double d = pos.distSqr(origin);
                if (d < bestDist) {
                    bestDist = d;
                    best = pos.immutable();
                }
            }
        }
        target = best;
        return target != null;
    }

    @Override
    public void start() {
        ticks = 0;
        mob.getNavigation().moveTo(target.getX() + 0.5, target.getY(), target.getZ() + 0.5, 0.9);
    }

    @Override
    public boolean canContinueToUse() {
        return target != null && ticks < 200 && mob.level().getBlockState(target).getBlock() instanceof MushroomBlock
                && !mob.isOrderedToSit();
    }

    @Override
    public void tick() {
        ticks++;
        mob.getLookControl().setLookAt(target.getX() + 0.5, target.getY() + 0.3, target.getZ() + 0.5);
        if (mob.distanceToSqr(target.getX() + 0.5, target.getY(), target.getZ() + 0.5) < 2.6) {
            mob.getNavigation().stop();
            if (mob.level() instanceof ServerLevel level) {
                BlockState state = level.getBlockState(target);
                mob.celebrate();
                level.sendParticles(ModParticles.SPORE.get(), target.getX() + 0.5, target.getY() + 0.5, target.getZ() + 0.5,
                        12, 0.3, 0.2, 0.3, 0.01);
                if (mob.getRandom().nextFloat() < 0.35F) {
                    FungusBlock.spread(level, target, state, mob.getRandom());
                }
            }
            target = null;
        }
    }

    @Override
    public void stop() {
        target = null;
    }
}
