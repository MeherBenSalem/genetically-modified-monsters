package com.nightbeam.sporeandstem.effect;

import com.nightbeam.sporeandstem.config.SporeConfig;
import com.nightbeam.sporeandstem.entity.ShamblerEntity;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.TickTask;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
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

    /** True when this entity cannot carry Mycosis at all. */
    public static boolean isImmune(LivingEntity entity) {
        return entity.getType().is(ModTags.Entities.FUNGAL) || entity.hasEffect(ModEffects.SPORE_WARD.get())
                || !SporeConfig.get().mycosisEnabled;
    }

    @Override
    public boolean isDurationEffectTick(int duration, int amplifier) {
        int interval = Math.max(10, SporeConfig.get().mycosisDamageInterval >> amplifier);
        return duration % interval == 0;
    }

    @Override
    public void applyEffectTick(LivingEntity entity, int amplifier) {
        if (isImmune(entity)) {
            // Removed on the next server task: the effect map is being iterated right now.
            if (entity.level() instanceof ServerLevel level) {
                MinecraftServer server = level.getServer();
                server.tell(new TickTask(server.getTickCount(), () -> entity.removeEffect(ModEffects.MYCOSIS.get())));
            }
            return;
        }
        if (entity.getHealth() > 1.0F) {
            entity.hurt(entity.damageSources().magic(), 1.0F);
        }
    }

    /**
     * Called by LivingEntityMixin when an infected entity is removed from the world: a killed one rises as a
     * Shambler once its death animation ends (the moment 1.21's {@code onMobRemoved} fires).
     */
    public static void onRemoved(LivingEntity entity, Entity.RemovalReason reason) {
        boolean deadPlayer = reason == Entity.RemovalReason.DISCARDED && entity.isDeadOrDying();
        if ((reason == Entity.RemovalReason.KILLED || deadPlayer)
                && entity.level() instanceof ServerLevel level
                && SporeConfig.get().mycosisRising
                && entity.getType().is(ModTags.Entities.MYCOSIS_RISERS)) {
            ShamblerEntity.riseFrom(level, entity);
        }
    }
}
