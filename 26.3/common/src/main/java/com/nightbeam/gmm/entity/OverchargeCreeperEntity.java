package com.nightbeam.gmm.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class OverchargeCreeperEntity extends MutantCreeperEntity {
    public OverchargeCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
        this.applyExplosionRadiusOverride();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes();
    }

    @Override
    protected float explosionRadiusOverride() {
        // Vanilla charged uses radius 3 * 2 = 6; 2x charged => 12.
        return 12.0F;
    }

    @Override
    public void tick() {
        if (this.tickCount == 1) {
            this.applyExplosionRadiusOverride();
        }
        super.tick();
    }
}
