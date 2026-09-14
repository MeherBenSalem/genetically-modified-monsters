package com.nightbeam.gmm.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class ClimbCreeperEntity extends MutantCreeperEntity {
    public ClimbCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes();
    }

    @Override
    protected boolean canClimbWalls() {
        return true;
    }

    @Override
    public void tick() {
        super.tick();
        if (this.horizontalCollision && canClimbWalls()) {
            this.setDeltaMovement(this.getDeltaMovement().x, 0.22D, this.getDeltaMovement().z);
        }
    }
}
