package com.nightbeam.gmm.entity.ai;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.target.TargetGoal;
import net.minecraft.world.entity.ai.targeting.TargetingConditions;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.player.Player;

import java.util.EnumSet;
import java.util.UUID;

public class PersistentTargetGoal extends TargetGoal {
    private final Creeper creeper;
    private final TargetingConditions conditions = TargetingConditions.forCombat().ignoreLineOfSight().range(64.0D);
    private UUID lockedId;
    private LivingEntity lockedTarget;
    private int recheck;

    public PersistentTargetGoal(Creeper creeper) {
        super(creeper, false, false);
        this.creeper = creeper;
        this.setFlags(EnumSet.of(Flag.TARGET));
    }

    @Override
    public boolean canUse() {
        LivingEntity current = creeper.getTarget();
        if (current instanceof Player player && player.isAlive() && !player.isCreative() && !player.isSpectator()) {
            lockedId = player.getUUID();
            lockedTarget = player;
            return true;
        }
        if (lockedId != null) {
            Player player = creeper.level().getPlayerByUUID(lockedId);
            if (player != null && player.isAlive() && !player.isCreative() && !player.isSpectator()) {
                lockedTarget = player;
                return true;
            }
        }
        Player nearest = creeper.level().getNearestPlayer(conditions, creeper);
        if (nearest != null) {
            lockedId = nearest.getUUID();
            lockedTarget = nearest;
            return true;
        }
        return false;
    }

    @Override
    public void start() {
        creeper.setTarget(lockedTarget);
        recheck = 0;
        super.start();
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity target = creeper.getTarget();
        if (target instanceof Player player && player.isAlive() && !player.isCreative() && !player.isSpectator()) {
            lockedId = player.getUUID();
            lockedTarget = player;
            return true;
        }
        if (lockedId == null) {
            return false;
        }
        Player player = creeper.level().getPlayerByUUID(lockedId);
        if (player == null || !player.isAlive() || player.isCreative() || player.isSpectator()) {
            return false;
        }
        creeper.setTarget(player);
        lockedTarget = player;
        return true;
    }

    @Override
    public void tick() {
        if (++recheck >= 10 && lockedId != null) {
            recheck = 0;
            Player player = creeper.level().getPlayerByUUID(lockedId);
            if (player != null) {
                creeper.setTarget(player);
                creeper.getNavigation().moveTo(player, 1.25D);
            }
        }
    }
}
