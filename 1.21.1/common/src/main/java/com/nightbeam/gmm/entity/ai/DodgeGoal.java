package com.nightbeam.gmm.entity.ai;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

public class DodgeGoal extends Goal {
    private final Creeper creeper;
    private int ticks;

    public DodgeGoal(Creeper creeper) {
        this.creeper = creeper;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        return creeper.getLastHurtByMob() != null && creeper.getLastHurtByMobTimestamp() + 20 > creeper.tickCount
                && creeper.getRandom().nextInt(3) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return ticks > 0;
    }

    @Override
    public void start() {
        ticks = 12;
        LivingEntity attacker = creeper.getLastHurtByMob();
        if (attacker == null) {
            return;
        }
        Vec3 away = creeper.position().subtract(attacker.position()).normalize().scale(0.7D);
        double side = creeper.getRandom().nextBoolean() ? 1.0D : -1.0D;
        Vec3 strafe = new Vec3(-away.z, 0.0D, away.x).scale(side * 0.55D);
        creeper.setDeltaMovement(creeper.getDeltaMovement().add(away.add(strafe).add(0.0D, 0.25D, 0.0D)));
        creeper.hasImpulse = true;
    }

    @Override
    public void tick() {
        ticks--;
    }
}
