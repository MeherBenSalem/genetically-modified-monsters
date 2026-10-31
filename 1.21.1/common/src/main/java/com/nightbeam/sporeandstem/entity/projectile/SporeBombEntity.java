package com.nightbeam.sporeandstem.entity.projectile;

import com.nightbeam.sporeandstem.entity.SporeClouds;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModItems;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;

/** A thrown Spore Bomb: bursts on impact into a cloud of Mycosis and Slowness (r 3, 6 s). */
public class SporeBombEntity extends ThrowableItemProjectile {

    public SporeBombEntity(EntityType<? extends SporeBombEntity> type, Level level) {
        super(type, level);
    }

    public SporeBombEntity(Level level, LivingEntity shooter) {
        super(ModEntities.SPORE_BOMB.get(), shooter, level);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.SPORE_BOMB.get();
    }

    @Override
    protected void onHit(HitResult result) {
        super.onHit(result);
        if (this.level() instanceof ServerLevel level) {
            LivingEntity owner = this.getOwner() instanceof LivingEntity living ? living : null;
            SporeClouds.spawn(level, result.getLocation(), 3.0F, 120, owner,
                    new MobEffectInstance(ModEffects.MYCOSIS.holder(), 300),
                    new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 120, 1));
            level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.SPORE_BOMB_BURST.get(),
                    SoundSource.NEUTRAL, 1.0F, 0.9F + this.random.nextFloat() * 0.2F);
            this.discard();
        }
    }
}
