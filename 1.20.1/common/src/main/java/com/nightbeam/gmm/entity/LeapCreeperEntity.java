package com.nightbeam.gmm.entity;

import com.nightbeam.gmm.entity.ai.LeapAttackGoal;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class LeapCreeperEntity extends MutantCreeperEntity {
    public LeapCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        AttributeSupplier.Builder builder = createBaseAttributes()
                .add(Attributes.MOVEMENT_SPEED, 0.27D)
                .add(Attributes.FOLLOW_RANGE, 28.0D);
        return builder;
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(1, new LeapAttackGoal(this, 1.15D));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (this.onGround() && this.getTarget() != null && this.random.nextInt(60) == 0) {
            this.setDeltaMovement(this.getDeltaMovement().add(0.0D, 0.55D, 0.0D));
            this.hasImpulse = true;
        }
    }
}
