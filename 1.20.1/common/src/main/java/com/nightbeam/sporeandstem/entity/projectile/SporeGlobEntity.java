package com.nightbeam.sporeandstem.entity.projectile;

import com.nightbeam.sporeandstem.effect.MycosisEffect;
import com.nightbeam.sporeandstem.entity.SporeClouds;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModItems;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;

/** A lobbed glob of spores (Sporemaw, Myceliarch): 3 damage on a hit and a small Mycosis cloud where it lands. */
public class SporeGlobEntity extends ThrowableItemProjectile {
    private float damage = 3.0F;

    public SporeGlobEntity(EntityType<? extends SporeGlobEntity> type, Level level) {
        super(type, level);
    }

    public SporeGlobEntity(Level level, LivingEntity shooter) {
        super(ModEntities.SPORE_GLOB.get(), shooter, level);
    }

    public SporeGlobEntity(Level level, double x, double y, double z) {
        super(ModEntities.SPORE_GLOB.get(), x, y, z, level);
    }

    public void setDamage(float damage) {
        this.damage = damage;
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.SPORE_GLOB.get();
    }

    @Override
    protected float getGravity() {
        return 0.05F;
    }

    @Override
    protected boolean canHitEntity(Entity target) {
        return super.canHitEntity(target) && !target.getType().is(ModTags.Entities.FUNGAL);
    }

    @Override
    public void tick() {
        super.tick();
        if (this.level().isClientSide && this.random.nextInt(2) == 0) {
            this.level().addParticle(ModParticles.SPORE.get(), this.getX(), this.getY() + 0.1, this.getZ(), 0.0, 0.0, 0.0);
        }
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        Entity target = result.getEntity();
        target.hurt(this.damageSources().mobProjectile(this, this.getOwner() instanceof LivingEntity l ? l : null), damage);
        if (target instanceof LivingEntity living && !MycosisEffect.isImmune(living)) {
            living.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.get(), 200), this.getOwner());
        }
    }

    @Override
    protected void onHit(HitResult result) {
        super.onHit(result);
        if (this.level() instanceof ServerLevel level) {
            LivingEntity owner = this.getOwner() instanceof LivingEntity living ? living : null;
            SporeClouds.spawn(level, result.getLocation(), 1.5F, 60, owner,
                    new MobEffectInstance(ModEffects.MYCOSIS.get(), 200));
            level.playSound(null, this.getX(), this.getY(), this.getZ(), ModSounds.SPORE_GLOB_SPLAT.get(),
                    SoundSource.HOSTILE, 0.8F, 0.9F + this.random.nextFloat() * 0.25F);
            this.discard();
        }
    }
}
