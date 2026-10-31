package com.nightbeam.sporeandstem.effect;

import com.nightbeam.sporeandstem.config.SporeConfig;
import com.nightbeam.sporeandstem.entity.ShamblerEntity;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;

/**
 * A slow fungal infection. Deals a point of damage at an interval (never below one health), ignored by fungal
 * creatures and by anyone under Spore Ward. Those in {@code #spore_and_stem:mycosis_risers} that die infected rise
 * again as Shamblers.
 */
public class MycosisEffect extends MobEffect {

    public MycosisEffect() {
        super(MobEffectCategory.HARMFUL, 0x7FB069);
    }

    /** Spore motes instead of the swirl. Resolved lazily: effects register before particle types on NeoForge. */
    @Override
    public ParticleOptions createParticleOptions(MobEffectInstance effect) {
        return ModParticles.SPORE.get();
    }

    /** True when this entity cannot carry Mycosis at all. */
    public static boolean isImmune(LivingEntity entity) {
        return entity.getType().is(ModTags.Entities.FUNGAL) || entity.hasEffect(ModEffects.SPORE_WARD.holder())
                || !SporeConfig.get().mycosisEnabled;
    }

    @Override
    public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {
        int interval = Math.max(10, SporeConfig.get().mycosisDamageInterval >> amplifier);
        return duration % interval == 0;
    }

    @Override
    public boolean applyEffectTick(LivingEntity entity, int amplifier) {
        if (isImmune(entity)) {
            return false; // removes the effect
        }
        if (entity.getHealth() > 1.0F) {
            entity.hurt(entity.damageSources().magic(), 1.0F);
        }
        return true;
    }

    @Override
    public void onMobRemoved(LivingEntity entity, int amplifier, Entity.RemovalReason reason) {
        boolean deadPlayer = reason == Entity.RemovalReason.DISCARDED && entity.isDeadOrDying();
        if ((reason == Entity.RemovalReason.KILLED || deadPlayer)
                && entity.level() instanceof ServerLevel level
                && SporeConfig.get().mycosisRising
                && entity.getType().is(ModTags.Entities.MYCOSIS_RISERS)) {
            ShamblerEntity.riseFrom(level, entity);
        }
    }
}
