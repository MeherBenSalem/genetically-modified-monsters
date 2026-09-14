package com.nightbeam.gmm.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

import java.lang.reflect.Field;

public abstract class MutantCreeperEntity extends Creeper {
    protected MutantCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createBaseAttributes() {
        return Creeper.createAttributes()
                .add(Attributes.MAX_HEALTH, 24.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.28D)
                .add(Attributes.FOLLOW_RANGE, 24.0D)
                .add(Attributes.JUMP_STRENGTH, 0.42D);
    }

    protected boolean isSilentMutant() {
        return false;
    }

    protected boolean canClimbWalls() {
        return false;
    }

    protected float explosionRadiusOverride() {
        return -1.0F;
    }

    @Override
    public boolean onClimbable() {
        return (canClimbWalls() && this.horizontalCollision) || super.onClimbable();
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isSilentMutant() ? null : super.getAmbientSound();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return isSilentMutant() ? null : super.getHurtSound(source);
    }

    @Override
    protected SoundEvent getDeathSound() {
        return isSilentMutant() ? SoundEvents.CREEPER_DEATH : super.getDeathSound();
    }

    @Override
    public void playSound(SoundEvent sound, float volume, float pitch) {
        if (isSilentMutant() && sound == SoundEvents.CREEPER_PRIMED) {
            return;
        }
        super.playSound(sound, volume, pitch);
    }

    protected void applyExplosionRadiusOverride() {
        float override = explosionRadiusOverride();
        if (override < 0.0F) {
            return;
        }
        try {
            Field field = Creeper.class.getDeclaredField("explosionRadius");
            field.setAccessible(true);
            field.setInt(this, Math.round(override));
        } catch (ReflectiveOperationException ignored) {
            try {
                for (Field field : Creeper.class.getDeclaredFields()) {
                    if (field.getType() == int.class && !field.getName().contains("swell") && !field.getName().contains("Swell")) {
                        field.setAccessible(true);
                        int current = field.getInt(this);
                        if (current == 3) {
                            field.setInt(this, Math.round(override));
                            break;
                        }
                    }
                }
            } catch (ReflectiveOperationException ignored2) {
            }
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
    }
}
