package com.nightbeam.sporeandstem.entity;

import com.nightbeam.sporeandstem.registry.ModEntities;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/** Shambler (placeholder until the creature is implemented). */
public class ShamblerEntity extends Monster {

    public ShamblerEntity(EntityType<? extends ShamblerEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 26.0);
    }

    /** The infected dead rise: a Shambler stands up where {@code corpse} fell. */
    public static void riseFrom(ServerLevel level, LivingEntity corpse) {
        ShamblerEntity shambler = ModEntities.SHAMBLER.get().create(level);
        if (shambler != null) {
            shambler.moveTo(corpse.getX(), corpse.getY(), corpse.getZ(), corpse.getYRot(), 0.0F);
            shambler.finalizeSpawn(level, level.getCurrentDifficultyAt(corpse.blockPosition()), MobSpawnType.CONVERSION, null);
            level.addFreshEntity(shambler);
        }
    }
}
