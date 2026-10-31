package com.nightbeam.sporeandstem.entity;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.effect.MycosisEffect;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The infected risen: a slow, lurching walker whose hits carry Mycosis. It does not burn, but it wilts in direct
 * sunlight (25% slower). The infected dead rise as Shamblers ({@link #riseFrom}), clawing up out of the ground.
 */
public class ShamblerEntity extends Monster {
    public static final byte EVENT_ATTACK = 103;
    private static final int RISE_TICKS = 36;
    private static final ResourceLocation WILT_ID = SporeAndStem.id("wilting");
    private static final EntityDataAccessor<Boolean> DATA_RISING = SynchedEntityData.defineId(ShamblerEntity.class,
            EntityDataSerializers.BOOLEAN);

    public final AnimationState attackState = new AnimationState();
    public final AnimationState riseState = new AnimationState();
    private int riseTicks;

    public ShamblerEntity(EntityType<? extends ShamblerEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 26.0).add(Attributes.ARMOR, 2.0)
                .add(Attributes.ATTACK_DAMAGE, 4.0).add(Attributes.MOVEMENT_SPEED, 0.23)
                .add(Attributes.FOLLOW_RANGE, 32.0).add(Attributes.KNOCKBACK_RESISTANCE, 0.1);
    }

    /** The infected dead rise: a Shambler claws its way up where {@code corpse} fell. */
    public static void riseFrom(ServerLevel level, LivingEntity corpse) {
        ShamblerEntity shambler = ModEntities.SHAMBLER.get().create(level);
        if (shambler == null) {
            return;
        }
        shambler.moveTo(corpse.getX(), corpse.getY(), corpse.getZ(), corpse.getYRot(), 0.0F);
        shambler.finalizeSpawn(level, level.getCurrentDifficultyAt(corpse.blockPosition()), MobSpawnType.CONVERSION, null);
        shambler.setRising(true);
        if (corpse.hasCustomName()) {
            shambler.setCustomName(corpse.getCustomName());
        }
        level.addFreshEntity(shambler);
        level.playSound(null, corpse.getX(), corpse.getY(), corpse.getZ(), ModSounds.SHAMBLER_RISE.get(),
                shambler.getSoundSource(), 1.0F, 0.9F + level.random.nextFloat() * 0.2F);
        level.sendParticles(ModParticles.SPORE.get(), corpse.getX(), corpse.getY() + 0.5, corpse.getZ(), 30, 0.4, 0.4, 0.4, 0.02);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(DATA_RISING, false);
    }

    public boolean isRising() {
        return this.entityData.get(DATA_RISING);
    }

    public void setRising(boolean rising) {
        this.entityData.set(DATA_RISING, rising);
        this.riseTicks = 0;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.8));
        this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 8.0F));
        this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    @Override
    protected boolean isImmobile() {
        return super.isImmobile() || this.isRising();
    }

    @Override
    public void tick() {
        super.tick();
        if (this.level().isClientSide) {
            if (this.isRising()) {
                riseState.startIfStopped(this.tickCount);
                BlockState ground = this.level().getBlockState(this.blockPosition().below());
                if (!ground.isAir() && this.random.nextInt(2) == 0) {
                    this.level().addParticle(new BlockParticleOption(ParticleTypes.BLOCK, ground),
                            this.getX() + (this.random.nextDouble() - 0.5) * 0.8, this.getY() + 0.1,
                            this.getZ() + (this.random.nextDouble() - 0.5) * 0.8, 0.0, 0.1, 0.0);
                }
            } else if (riseState.isStarted() && riseState.getAccumulatedTime() > 2000L) {
                riseState.stop();
            }
            if (this.random.nextInt(40) == 0) {
                this.level().addParticle(ModParticles.SPORE.get(), this.getX() + (this.random.nextDouble() - 0.5) * 0.6,
                        this.getY() + 1.9, this.getZ() + (this.random.nextDouble() - 0.5) * 0.6, 0.0, 0.0, 0.0);
            }
        }
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (!this.level().isClientSide) {
            if (this.isRising() && ++this.riseTicks >= RISE_TICKS) {
                this.setRising(false);
            }
            updateWilting();
        }
    }

    /** In direct sunlight a Shambler wilts: 25% slower. */
    private void updateWilting() {
        AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed == null || this.tickCount % 10 != 0) {
            return;
        }
        BlockPos eyes = BlockPos.containing(this.getX(), this.getEyeY(), this.getZ());
        boolean sunlit = this.level().isDay() && !this.level().isRaining() && this.level().canSeeSky(eyes)
                && this.getLightLevelDependentMagicValue() > 0.5F;
        boolean wilting = speed.hasModifier(WILT_ID);
        if (sunlit && !wilting) {
            speed.addTransientModifier(new AttributeModifier(WILT_ID, -0.25, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
        } else if (!sunlit && wilting) {
            speed.removeModifier(WILT_ID);
        }
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        this.level().broadcastEntityEvent(this, EVENT_ATTACK);
        this.playSound(ModSounds.SHAMBLER_ATTACK.get(), 1.0F, 0.9F + this.random.nextFloat() * 0.2F);
        boolean hit = super.doHurtTarget(target);
        if (hit && target instanceof LivingEntity living && !MycosisEffect.isImmune(living)) {
            living.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 160), this);
        }
        return hit;
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == EVENT_ATTACK) {
            attackState.start(this.tickCount);
        } else {
            super.handleEntityEvent(id);
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Rising", this.isRising());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.entityData.set(DATA_RISING, tag.getBoolean("Rising"));
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.SHAMBLER_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.SHAMBLER_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.SHAMBLER_DEATH.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        this.playSound(SoundEvents.ZOMBIE_STEP, 0.12F, 0.8F);
    }
}
