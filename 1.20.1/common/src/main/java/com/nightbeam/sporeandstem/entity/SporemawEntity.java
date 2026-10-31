package com.nightbeam.sporeandstem.entity;

import com.nightbeam.sporeandstem.entity.projectile.SporeGlobEntity;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * An ambush fungus. It lies burrowed with only its hood showing, rises when a player comes within 10 blocks, lobs an
 * arcing Spore Glob every two seconds, and after three hits (or once it loses its target) sinks away and resurfaces
 * up to 8 blocks off.
 */
public class SporemawEntity extends Monster {
    public static final int BURROWED = 0;
    public static final int EMERGING = 1;
    public static final int ACTIVE = 2;
    public static final int BURROWING = 3;
    public static final byte EVENT_SPIT = 104;
    private static final EntityDataAccessor<Integer> DATA_STATE = SynchedEntityData.defineId(SporemawEntity.class,
            EntityDataSerializers.INT);
    private static final EntityDimensions BURROWED_SIZE = EntityDimensions.scalable(0.9F, 0.35F);

    public final AnimationState emergeState = new AnimationState();
    public final AnimationState burrowState = new AnimationState();
    public final AnimationState spitState = new AnimationState();
    private int stateTicks;
    private int spitCooldown = 30;
    private int pendingShot = -1;
    private int hitsTaken;
    private int lostTicks;

    public SporemawEntity(EntityType<? extends SporemawEntity> type, Level level) {
        super(type, level);
        this.xpReward = 6;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 20.0).add(Attributes.ARMOR, 4.0)
                .add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 18.0);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_STATE, BURROWED);
    }

    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    public int getState() {
        return this.entityData.get(DATA_STATE);
    }

    private void setState(int state) {
        this.entityData.set(DATA_STATE, state);
        this.stateTicks = 0;
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (DATA_STATE.equals(key)) {
            this.refreshDimensions();
            if (this.level().isClientSide) {
                int state = getState();
                emergeState.stop();
                burrowState.stop();
                if (state == EMERGING) {
                    emergeState.start(this.tickCount);
                } else if (state == BURROWING) {
                    burrowState.start(this.tickCount);
                }
            }
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return getState() == BURROWED ? BURROWED_SIZE : super.getDimensions(pose);
    }

    // ---- behaviour ----------------------------------------------------------------------------------------------

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        stateTicks++;
        LivingEntity target = this.getTarget();
        boolean valid = target != null && target.isAlive() && !(target instanceof Player p && (p.isCreative() || p.isSpectator()));
        switch (getState()) {
            case BURROWED -> {
                if (valid && stateTicks > 20 && this.distanceToSqr(target) < 100.0) {
                    setState(EMERGING);
                    this.playSound(ModSounds.SPOREMAW_EMERGE.get(), 1.0F, 1.0F);
                    hitsTaken = 0;
                    lostTicks = 0;
                }
            }
            case EMERGING -> {
                dust(3);
                if (stateTicks >= 20) {
                    setState(ACTIVE);
                    spitCooldown = 15;
                }
            }
            case ACTIVE -> {
                if (valid) {
                    this.getLookControl().setLookAt(target, 30.0F, 30.0F);
                    boolean sees = this.getSensing().hasLineOfSight(target);
                    lostTicks = sees ? 0 : lostTicks + 1;
                    if (sees && --spitCooldown <= 0 && this.distanceToSqr(target) < 256.0 && pendingShot < 0) {
                        this.level().broadcastEntityEvent(this, EVENT_SPIT);
                        pendingShot = 7;
                        spitCooldown = 40;
                    }
                } else {
                    lostTicks++;
                }
                if (pendingShot >= 0 && --pendingShot == 0) {
                    pendingShot = -1;
                    if (valid) {
                        spitAt(target);
                    }
                }
                if (hitsTaken >= 3 || lostTicks > 100) {
                    setState(BURROWING);
                    this.playSound(ModSounds.SPOREMAW_BURROW.get(), 1.0F, 1.0F);
                }
            }
            case BURROWING -> {
                dust(3);
                if (stateTicks >= 16) {
                    relocate();
                    setState(BURROWED);
                }
            }
            default -> setState(BURROWED);
        }
    }

    /** Lobs a glob on a ballistic arc that lands on the target (gravity 0.05, drag 0.99 per tick). */
    private void spitAt(LivingEntity target) {
        SporeGlobEntity glob = new SporeGlobEntity(this.level(), this);
        Vec3 from = new Vec3(this.getX(), this.getY() + 1.15, this.getZ());
        glob.setPos(from);
        Vec3 to = target.position().add(target.getDeltaMovement().scale(8.0)).add(0.0, target.getBbHeight() * 0.4, 0.0);
        double dx = to.x - from.x;
        double dz = to.z - from.z;
        double horizontal = Math.max(0.5, Math.sqrt(dx * dx + dz * dz));
        double speed = 0.75;
        double ticks = horizontal / speed;
        double vy = (to.y - from.y) / ticks + 0.5 * 0.05 * ticks;
        double spread = 0.04;
        glob.setDeltaMovement(dx / horizontal * speed + this.random.triangle(0, spread), vy,
                dz / horizontal * speed + this.random.triangle(0, spread));
        this.level().addFreshEntity(glob);
        this.playSound(ModSounds.SPOREMAW_SPIT.get(), 1.0F, 0.9F + this.random.nextFloat() * 0.2F);
    }

    /** Resurfaces at a free spot on solid ground within 8 blocks. */
    private void relocate() {
        BlockPos origin = this.blockPosition();
        for (int i = 0; i < 24; i++) {
            BlockPos candidate = origin.offset(this.random.nextInt(17) - 8, this.random.nextInt(7) - 3, this.random.nextInt(17) - 8);
            for (int dy = 2; dy >= -3; dy--) {
                BlockPos pos = candidate.above(dy);
                BlockPos below = pos.below();
                if (this.level().getBlockState(below).isFaceSturdy(this.level(), below, Direction.UP)
                        && this.level().isEmptyBlock(pos) && this.level().isEmptyBlock(pos.above())
                        && this.level().getFluidState(pos).isEmpty()) {
                    this.teleportTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5);
                    return;
                }
            }
        }
    }

    private void dust(int count) {
        if (this.level() instanceof ServerLevel level) {
            BlockState ground = level.getBlockState(this.blockPosition().below());
            if (!ground.isAir()) {
                level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), this.getX(), this.getY() + 0.1,
                        this.getZ(), count, 0.4, 0.05, 0.4, 0.05);
            }
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        int state = getState();
        if (state == BURROWED && !source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            amount *= 0.5F;
        }
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide) {
            if (state == ACTIVE) {
                hitsTaken++;
            } else if (state == BURROWED && this.isAlive()) {
                setState(EMERGING);
                this.playSound(ModSounds.SPOREMAW_EMERGE.get(), 1.0F, 1.0F);
            }
        }
        return hurt;
    }

    @Override
    public void tick() {
        super.tick();
        if (this.level().isClientSide && getState() == ACTIVE && this.random.nextInt(12) == 0) {
            this.level().addParticle(ModParticles.SPORE.get(), this.getX() + (this.random.nextDouble() - 0.5) * 0.8,
                    this.getY() + 1.1, this.getZ() + (this.random.nextDouble() - 0.5) * 0.8, 0.0, 0.01, 0.0);
        }
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == EVENT_SPIT) {
            spitState.start(this.tickCount);
        } else {
            super.handleEntityEvent(id);
        }
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    protected void doPush(net.minecraft.world.entity.Entity entity) {
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Burrow", getState() == BURROWED || getState() == BURROWING ? BURROWED : ACTIVE);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.entityData.set(DATA_STATE, tag.getInt("Burrow"));
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return getState() == BURROWED ? null : ModSounds.SPOREMAW_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.SPOREMAW_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.SPOREMAW_DEATH.get();
    }

    /** Eye at 1 of 1.3 blocks (scaled with the body, so babies keep the proportion). */
    @Override
    protected float getStandingEyeHeight(Pose pose, EntityDimensions dimensions) {
        if (dimensions == BURROWED_SIZE) {
            return 0.25F;
        }
        return dimensions.height * 0.7692F;
    }
}
