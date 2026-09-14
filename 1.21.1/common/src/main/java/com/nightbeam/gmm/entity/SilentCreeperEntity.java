package com.nightbeam.gmm.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class SilentCreeperEntity extends MutantCreeperEntity {
    public SilentCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes()
                .add(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED, 0.30D);
    }

    @Override
    protected boolean isSilentMutant() {
        return true;
    }
}
