package com.nightbeam.gmm.entity;

import com.nightbeam.gmm.entity.ai.DodgeGoal;
import com.nightbeam.gmm.entity.ai.HazardAvoidGoal;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class AdaptiveCreeperEntity extends MutantCreeperEntity {
    public AdaptiveCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes()
                .add(Attributes.MOVEMENT_SPEED, 0.34D)
                .add(Attributes.FOLLOW_RANGE, 32.0D);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(1, new DodgeGoal(this));
        this.goalSelector.addGoal(1, new HazardAvoidGoal(this));
    }
}
