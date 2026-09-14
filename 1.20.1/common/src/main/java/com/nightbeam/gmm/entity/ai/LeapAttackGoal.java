package com.nightbeam.gmm.entity.ai;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Creeper;

import java.util.EnumSet;

public class LeapAttackGoal extends Goal {
    private final Creeper creeper;
    private final double leapStrength;
    private int cooldown;

    public LeapAttackGoal(Creeper creeper, double leapStrength) {
        this.creeper = creeper;
        this.leapStrength = leapStrength;
        this.setFlags(EnumSet.of(Flag.JUMP, Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (cooldown > 0) {
            cooldown--;
            return false;
        }
        LivingEntity target = creeper.getTarget();
        if (target == null || !creeper.onGround()) {
            return false;
        }
        double dist = creeper.distanceToSqr(target);
        return dist > 9.0D && dist < 100.0D && creeper.getRandom().nextInt(8) == 0;
    }

    @Override
    public void start() {
        LivingEntity target = creeper.getTarget();
        if (target == null) {
            return;
        }
        double dx = target.getX() - creeper.getX();
        double dz = target.getZ() - creeper.getZ();
        double len = Math.sqrt(dx * dx + dz * dz);
        if (len > 1.0E-4D) {
            creeper.setDeltaMovement(dx / len * 0.85D, leapStrength, dz / len * 0.85D);
        } else {
            creeper.setDeltaMovement(0.0D, leapStrength, 0.0D);
        }
        creeper.hasImpulse = true;
        cooldown = 40;
    }
}
