package com.nightbeam.sporeandstem.entity;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.Pose;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.config.SporeConfig;
import com.nightbeam.sporeandstem.effect.MycosisEffect;
import com.nightbeam.sporeandstem.entity.boss.RootSpikes;
import com.nightbeam.sporeandstem.entity.projectile.SporeGlobEntity;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.UUID;

/**
 * The Myceliarch, ruler of the mycelium (docs/DESIGN.md §4.1).
 *
 * <p>A server-side state machine drives the fight; the state is synced so the client plays the matching keyframed
 * animation. Every attack has a wind-up the player can read (pose, particles marking the danger zone, sound) before
 * it lands. Its health and damage come from the config.
 */
public class MyceliarchEntity extends Monster {
    public static final byte IDLE = 0;
    public static final byte EMERGING = 1;
    public static final byte SLAM = 2;
    public static final byte ERUPT = 3;
    public static final byte NOVA = 4;
    public static final byte BROOD = 5;
    public static final byte ROAR = 6;
    public static final byte RAIN = 7;
    /** Ticks each state lasts; they match the animation lengths. */
    private static final int[] DURATION = {0, 108, 32, 36, 48, 40, 40, 28};
    /** Emerging: the first ticks are a ritual underground before it hauls itself out. */
    public static final int RITUAL_TICKS = 60;
    private static final int SLAM_HIT = 15;
    private static final int ERUPT_HIT = 14;
    private static final int NOVA_HIT = 30;
    private static final int BROOD_HIT = 18;
    private static final int ROAR_HIT = 12;
    private static final int RAIN_HIT = 12;
    private static final int DEATH_TICKS = 60;
    private static final int MAX_MINIONS = 6;
    private static final double LEASH = 40.0;

    private static final EntityDataAccessor<Byte> DATA_STATE = SynchedEntityData.defineId(MyceliarchEntity.class,
            EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Boolean> DATA_BLOOM = SynchedEntityData.defineId(MyceliarchEntity.class,
            EntityDataSerializers.BOOLEAN);
    private static final java.util.UUID BLOOM_SPEED = java.util.UUID.fromString("c1e8a6d2-4f7b-4b39-8d15-6a2f0e9b7c53");

    public final AnimationState idleState = new AnimationState();
    public final AnimationState emergeState = new AnimationState();
    public final AnimationState slamState = new AnimationState();
    public final AnimationState eruptState = new AnimationState();
    public final AnimationState novaState = new AnimationState();
    public final AnimationState broodState = new AnimationState();
    public final AnimationState roarState = new AnimationState();
    public final AnimationState rainState = new AnimationState();
    public final AnimationState deathState = new AnimationState();

    private final ServerBossEvent bossEvent = new ServerBossEvent(this.getDisplayName(), BossEvent.BossBarColor.GREEN,
            BossEvent.BossBarOverlay.NOTCHED_10);
    private int stateTicks;
    private int globalCooldown = 30;
    private int slamCooldown;
    private int eruptCooldown = 60;
    private int novaCooldown = 200;
    private int broodCooldown = 320;
    private int rainCooldown;
    private int rainTicks;
    private int noTargetTicks;
    private float attackYaw;
    private Vec3 aim = Vec3.ZERO;
    private final List<Vec3> broodSpots = new ArrayList<>();
    private final List<UUID> minions = new ArrayList<>();
    @Nullable
    private BlockPos home;
    @Nullable
    private UUID summoner;
    @Nullable
    private DamageSource pendingDeathSource;
    private int collapseTicks;

    public MyceliarchEntity(EntityType<? extends MyceliarchEntity> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.5F);
        this.xpReward = 250;
        this.setPersistenceRequired();
        this.bossEvent.setVisible(false);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, SporeConfig.get().myceliarchHealth)
                .add(Attributes.ARMOR, 10.0)
                .add(Attributes.ATTACK_DAMAGE, 14.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 48.0)
                .add(Attributes.MOVEMENT_SPEED, 0.24);
    }

    // ---------------------------------------------------------------------------------------------- summoning

    /**
     * Called by the Fruiting Heart. The Myceliarch spends three seconds rising through the earth (roots and spores
     * break the surface) and then hauls itself out. Fails, with a message, when there is no room or another
     * Myceliarch is already near.
     */
    public static boolean summon(ServerLevel level, BlockPos pos, @Nullable Player summoner) {
        if (!level.getEntitiesOfClass(MyceliarchEntity.class, new AABB(pos).inflate(96.0)).isEmpty()) {
            tell(summoner, "already");
            return false;
        }
        for (BlockPos p : BlockPos.betweenClosed(pos.offset(-1, 0, -1), pos.offset(1, 4, 1))) {
            if (!level.getBlockState(p).getCollisionShape(level, p).isEmpty()) {
                tell(summoner, "no_room");
                return false;
            }
        }
        MyceliarchEntity boss = ModEntities.MYCELIARCH.get().create(level);
        if (boss == null) {
            return false;
        }
        float yaw = level.random.nextFloat() * 360.0F;
        if (summoner != null) {
            double dx = summoner.getX() - (pos.getX() + 0.5);
            double dz = summoner.getZ() - (pos.getZ() + 0.5);
            yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        }
        boss.moveTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, yaw, 0.0F);
        boss.setYHeadRot(yaw);
        boss.yBodyRot = yaw;
        boss.home = pos.immutable();
        boss.summoner = summoner == null ? null : summoner.getUUID();
        boss.restrictTo(pos, (int) LEASH);
        boss.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.TRIGGERED, null, null);
        boss.setState(EMERGING);
        if (!level.addFreshEntity(boss)) {
            return false;
        }
        level.playSound(null, pos, ModSounds.FRUITING_HEART_USE.get(), SoundSource.HOSTILE, 1.5F, 0.8F);
        boss.announce("stirs", ChatFormatting.GRAY);
        return true;
    }

    private static void tell(@Nullable Player player, String key) {
        if (player != null) {
            player.displayClientMessage(Component.translatable("message.spore_and_stem.myceliarch." + key)
                    .withStyle(ChatFormatting.GRAY), true);
        }
    }

    private void announce(String key, ChatFormatting colour) {
        for (Player player : this.level().players()) {
            if (player.distanceToSqr(this) < 64 * 64) {
                player.displayClientMessage(Component.translatable("message.spore_and_stem.myceliarch." + key)
                        .withStyle(colour), true);
            }
        }
    }

    // ---------------------------------------------------------------------------------------------- state

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_STATE, IDLE);
        this.entityData.define(DATA_BLOOM, false);
    }

    public byte getState() {
        return this.entityData.get(DATA_STATE);
    }

    private void setState(byte state) {
        this.entityData.set(DATA_STATE, state);
        this.stateTicks = 0;
    }

    /** Second bloom: at half health it blooms again, faster and brighter. */
    public boolean isBloom() {
        return this.entityData.get(DATA_BLOOM);
    }

    public boolean isEmerging() {
        return getState() == EMERGING;
    }

    private boolean isUntouchable() {
        byte s = getState();
        return s == EMERGING || s == ROAR;
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (DATA_STATE.equals(key) && this.level().isClientSide) {
            AnimationState[] actions = {emergeState, slamState, eruptState, novaState, broodState, roarState, rainState};
            for (AnimationState a : actions) {
                a.stop();
            }
            byte s = getState();
            if (s > IDLE && s - 1 < actions.length) {
                actions[s - 1].start(this.tickCount);
            }
        }
    }

    private int cooldown(int base) {
        return isBloom() ? Math.round(base * 0.6F) : base;
    }

    private float damage(float base) {
        return base * (float) SporeConfig.get().myceliarchDamageMultiplier;
    }

    // ---------------------------------------------------------------------------------------------- goals

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new ChaseGoal());
        this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.7) {
            @Override
            public boolean canUse() {
                return getState() == IDLE && super.canUse();
            }
        });
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 24.0F));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
    }

    /** Walks into striking range while idle; attacks are chosen in customServerAiStep. */
    private final class ChaseGoal extends Goal {
        private int repath;

        ChaseGoal() {
            this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity target = getTarget();
            return getState() == IDLE && target != null && target.isAlive();
        }

        @Override
        public void stop() {
            getNavigation().stop();
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity target = getTarget();
            if (target == null) {
                return;
            }
            getLookControl().setLookAt(target, 30.0F, 30.0F);
            double reach = 3.2 + target.getBbWidth() / 2;
            if (distanceTo(target) > reach) {
                if (--this.repath <= 0) {
                    this.repath = 8;
                    getNavigation().moveTo(target, 1.0);
                }
            } else {
                getNavigation().stop();
            }
        }
    }

    // ---------------------------------------------------------------------------------------------- the fight

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        ServerLevel level = (ServerLevel) this.level();
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
        tickMinions(level);
        tickRain(level);
        byte state = getState();
        if (state != IDLE) {
            this.stateTicks++;
            tickState(level, state, this.stateTicks);
            if (this.stateTicks >= DURATION[state] && getState() == state) {
                endState(state);
            }
            return;
        }
        this.globalCooldown--;
        this.slamCooldown--;
        this.eruptCooldown--;
        this.novaCooldown--;
        this.broodCooldown--;
        this.rainCooldown--;
        LivingEntity target = getTarget();
        if (target != null && (!target.isAlive() || (this.home != null && target.distanceToSqr(Vec3.atCenterOf(this.home)) > LEASH * LEASH))) {
            setTarget(null);
            target = null;
        }
        if (target == null) {
            if (++this.noTargetTicks > 60 && this.home != null && this.blockPosition().distSqr(this.home) > 100
                    && getNavigation().isDone()) {
                getNavigation().moveTo(this.home.getX() + 0.5, this.home.getY(), this.home.getZ() + 0.5, 0.9);
            }
            return;
        }
        this.noTargetTicks = 0;
        if (this.globalCooldown <= 0) {
            chooseAttack(target);
        }
    }

    private void chooseAttack(LivingEntity target) {
        double dist = this.distanceTo(target) - target.getBbWidth() / 2;
        if (dist <= 4.4 && this.slamCooldown <= 0) {
            begin(SLAM, target);
        } else if (this.novaCooldown <= 0 && dist <= 9.0) {
            begin(NOVA, target);
        } else if (this.broodCooldown <= 0 && countMinions() < MAX_MINIONS) {
            begin(BROOD, target);
        } else if (isBloom() && this.rainCooldown <= 0) {
            begin(RAIN, target);
        } else if (dist >= 5.5 && dist <= 20.0 && this.eruptCooldown <= 0 && this.hasLineOfSight(target)) {
            begin(ERUPT, target);
        }
    }

    private void begin(byte state, @Nullable LivingEntity target) {
        setState(state);
        getNavigation().stop();
        if (target != null) {
            this.aim = target.position();
            faceTowards(this.aim);
        }
        switch (state) {
            case SLAM -> this.slamCooldown = cooldown(50);
            case ERUPT -> this.eruptCooldown = cooldown(110);
            case NOVA -> this.novaCooldown = cooldown(300);
            case BROOD -> this.broodCooldown = cooldown(500);
            case RAIN -> this.rainCooldown = cooldown(400);
            default -> {
            }
        }
    }

    private void endState(byte state) {
        setState(IDLE);
        this.globalCooldown = cooldown(state == EMERGING ? 30 : 22);
        if (state == EMERGING) {
            this.bossEvent.setVisible(true);
        }
    }

    private void faceTowards(Vec3 pos) {
        double dx = pos.x - this.getX();
        double dz = pos.z - this.getZ();
        this.attackYaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0F;
        holdYaw();
    }

    private void holdYaw() {
        this.setYRot(this.attackYaw);
        this.yBodyRot = this.attackYaw;
        this.setYHeadRot(this.attackYaw);
    }

    private Vec3 forward(double distance) {
        float rad = this.attackYaw * Mth.DEG_TO_RAD;
        return this.position().add(-Mth.sin(rad) * distance, 0.0, Mth.cos(rad) * distance);
    }

    private void tickState(ServerLevel level, byte state, int t) {
        if (state != EMERGING) {
            holdYaw();
        }
        switch (state) {
            case EMERGING -> tickEmerging(level, t);
            case SLAM -> tickSlam(level, t);
            case ERUPT -> tickErupt(level, t);
            case NOVA -> tickNova(level, t);
            case BROOD -> tickBrood(level, t);
            case ROAR -> tickRoar(level, t);
            case RAIN -> {
                if (t == 1) {
                    play(ModSounds.MYCELIARCH_SPORE_NOVA.get(), 1.4F, 1.5F);
                }
                if (t < RAIN_HIT) {
                    level.sendParticles(ModParticles.GLOW_SPORE.get(), getX(), getY() + 3.6, getZ(), 4, 1.2, 0.2, 1.2, 0.02);
                }
                if (t == RAIN_HIT) {
                    this.rainTicks = 100;
                    level.sendParticles(ModParticles.GLOW_SPORE.get(), getX(), getY() + 4.4, getZ(), 40, 0.6, 0.3, 0.6, 0.25);
                }
            }
            default -> {
            }
        }
    }

    private void tickEmerging(ServerLevel level, int t) {
        double x = getX();
        double y = getY();
        double z = getZ();
        BlockState ground = groundState();
        if (t == 1) {
            play(ModSounds.MYCELIARCH_EMERGE.get(), 2.5F, 0.8F);
        }
        if (t < RITUAL_TICKS) {
            // The ritual: the earth cracks in a widening ring, spores rise in a closing column, roots break through.
            double r = 3.6 - t * 0.04;
            for (int i = 0; i < 3; i++) {
                double a = this.random.nextDouble() * Math.PI * 2;
                level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), x + Math.cos(a) * r, y + 0.1,
                        z + Math.sin(a) * r, 2, 0.1, 0.05, 0.1, 0.1);
            }
            level.sendParticles(ModParticles.GLOW_SPORE.get(), x, y + 0.2, z, 3, r * 0.35, 0.05, r * 0.35, 0.03);
            level.sendParticles(ModParticles.SPORE.get(), x, y + 0.3 + t * 0.03, z, 2, 0.6, 0.2, 0.6, 0.02);
            if (t > 8 && t % 7 == 0) {
                double a = this.random.nextDouble() * Math.PI * 2;
                double d = 2.4 + this.random.nextDouble() * 1.6;
                RootSpikes.spawn(level, this, x + Math.cos(a) * d, z + Math.sin(a) * d, y - 2, y + 2, 0, 0.0F, 0, true);
            }
            if (t % 20 == 0) {
                play(ModSounds.MYCELIARCH_STEP.get(), 1.6F, 0.5F + t * 0.005F);
            }
        } else {
            if (t == RITUAL_TICKS) {
                play(ModSounds.MYCELIARCH_EMERGE.get(), 3.0F, 1.0F);
                play(ModSounds.MYCELIARCH_ROOT_ERUPT.get(), 2.0F, 0.8F);
                RootSpikes.ring(level, this, x, z, y, 3.0, 9, 0, 0.0F, 0, true);
                this.bossEvent.setVisible(true);
                announce("rises", ChatFormatting.DARK_AQUA);
            }
            if (t % 2 == 0) {
                level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), x, y + 0.2, z, 10, 1.1, 0.1, 1.1, 0.2);
            }
            if (t == 97) {
                play(ModSounds.MYCELIARCH_ROAR.get(), 3.0F, 0.9F);
                shove(level, 8.0, 0.6, 0.25, false);
            }
        }
    }

    private void tickSlam(ServerLevel level, int t) {
        Vec3 impact = forward(2.8);
        if (t == 1) {
            play(ModSounds.MYCELIARCH_AMBIENT.get(), 2.0F, 0.6F);
        }
        if (t < SLAM_HIT && t % 2 == 0) {
            // Mark the strike zone on the ground.
            ring(level, ModParticles.SPORE.get(), impact, 2.6, 14);
        }
        if (t == SLAM_HIT) {
            play(ModSounds.MYCELIARCH_SLAM.get(), 3.0F, 0.9F + this.random.nextFloat() * 0.15F);
            level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, groundState()), impact.x, impact.y + 0.2, impact.z,
                    60, 1.4, 0.2, 1.4, 0.25);
            level.sendParticles(ModParticles.SPORE.get(), impact.x, impact.y + 0.5, impact.z, 40, 1.5, 0.4, 1.5, 0.08);
            level.sendParticles(ParticleTypes.EXPLOSION, impact.x, impact.y + 0.3, impact.z, 2, 0.6, 0.1, 0.6, 0.0);
            float dmg = damage((float) this.getAttributeValue(Attributes.ATTACK_DAMAGE));
            for (LivingEntity e : victims(impact, 2.8, -1.0, 3.5)) {
                if (e.hurt(this.damageSources().mobAttack(this), dmg)) {
                    Vec3 push = e.position().subtract(this.position()).multiply(1, 0, 1).normalize().scale(1.25);
                    e.push(push.x, 0.55, push.z);
                    e.hurtMarked = true;
                }
            }
            RootSpikes.ring(level, this, impact.x, impact.z, impact.y, 3.4, 8, 3, damage(6.0F), 30, false);
        }
    }

    private void tickErupt(ServerLevel level, int t) {
        if (t == 1) {
            play(ModSounds.MYCELIARCH_AMBIENT.get(), 2.0F, 0.75F);
        }
        LivingEntity target = getTarget();
        if (t <= 10 && target != null) {
            // Tracks the target through the wind-up, then commits.
            this.aim = target.position();
            faceTowards(this.aim);
        }
        if (t < ERUPT_HIT && t % 2 == 0) {
            level.sendParticles(ModParticles.GLOW_SPORE.get(), forward(1.6).x, getY() + 0.2, forward(1.6).z, 4, 0.4, 0.1, 0.4, 0.04);
        }
        if (t == ERUPT_HIT) {
            play(ModSounds.MYCELIARCH_ROOT_ERUPT.get(), 3.0F, 0.9F);
            Vec3 hand = forward(1.6);
            level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, groundState()), hand.x, getY() + 0.2, hand.z,
                    30, 0.6, 0.2, 0.6, 0.2);
            RootSpikes.line(level, this, getX(), getZ(), Math.min(getY(), this.aim.y) , this.attackYaw * Mth.DEG_TO_RAD, 12, 2.0,
                    1.35, damage(8.0F), 40);
        }
    }

    private void tickNova(ServerLevel level, int t) {
        if (t == 1) {
            play(ModSounds.MYCELIARCH_AMBIENT.get(), 2.5F, 0.55F);
        }
        Vec3 cap = this.position().add(0, 3.9, 0);
        if (t < NOVA_HIT) {
            // Spores are drawn in towards the swelling cap; the danger ring pulses on the ground.
            for (int i = 0; i < 4; i++) {
                double a = this.random.nextDouble() * Math.PI * 2;
                double r = 5.0 + this.random.nextDouble() * 2.0;
                Vec3 from = cap.add(Math.cos(a) * r, -1.0 - this.random.nextDouble() * 2.0, Math.sin(a) * r);
                Vec3 v = cap.subtract(from).scale(0.12);
                level.sendParticles(ModParticles.GLOW_SPORE.get(), from.x, from.y, from.z, 0, v.x, v.y, v.z, 1.0);
            }
            if (t % 4 == 0) {
                ring(level, ModParticles.SPORE.get(), this.position(), 7.0, 36);
            }
        }
        if (t == NOVA_HIT) {
            play(ModSounds.MYCELIARCH_SPORE_NOVA.get(), 3.0F, 0.9F);
            for (LivingEntity e : victims(this.position(), 7.0, -2.0, 5.0)) {
                if (!MycosisEffect.isImmune(e)) {
                    e.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.get(), 200, 1), this);
                }
            }
            shove(level, 7.0, 1.6, 0.4, false);
            SporeClouds.spawn(level, this.position(), 3.5F, 70, this, new MobEffectInstance(ModEffects.MYCOSIS.get(), 120));
        }
        if (t >= NOVA_HIT && t <= NOVA_HIT + 8) {
            // The spore wave rolls outward.
            ring(level, ModParticles.SPORE.get(), this.position().add(0, 0.6, 0), 1.0 + (t - NOVA_HIT) * 0.85, 40);
            ring(level, ModParticles.GLOW_SPORE.get(), this.position().add(0, 1.2, 0), 0.6 + (t - NOVA_HIT) * 0.8, 20);
        }
    }

    private void tickBrood(ServerLevel level, int t) {
        if (t == 1) {
            play(ModSounds.MYCELIARCH_ROAR.get(), 2.0F, 1.35F);
            this.broodSpots.clear();
            int count = Math.min(3, MAX_MINIONS - countMinions());
            for (int i = 0; i < count * 4 && this.broodSpots.size() < count; i++) {
                double a = this.random.nextDouble() * Math.PI * 2;
                double d = 3.5 + this.random.nextDouble() * 3.0;
                double x = getX() + Math.cos(a) * d;
                double z = getZ() + Math.sin(a) * d;
                double y = RootSpikes.floor(level, x, z, getY() - 4, getY() + 3);
                if (!Double.isNaN(y)) {
                    this.broodSpots.add(new Vec3(x, y, z));
                }
            }
        }
        if (t < BROOD_HIT) {
            for (Vec3 spot : this.broodSpots) {
                level.sendParticles(ModParticles.SPORE.get(), spot.x, spot.y + 0.1, spot.z, 2, 0.3, 0.05, 0.3, 0.02);
                if (t % 3 == 0) {
                    level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, groundState()), spot.x, spot.y + 0.1, spot.z,
                            3, 0.3, 0.05, 0.3, 0.1);
                }
            }
        }
        if (t == BROOD_HIT) {
            play(ModSounds.MYCELIARCH_SLAM.get(), 2.0F, 1.2F);
            LivingEntity target = getTarget();
            for (int i = 0; i < this.broodSpots.size(); i++) {
                Vec3 spot = this.broodSpots.get(i);
                EntityType<? extends Mob> type = i == 2 ? ModEntities.SHAMBLER.get() : ModEntities.BLOATSHROOM.get();
                Mob minion = type.create(level);
                if (minion == null) {
                    continue;
                }
                minion.moveTo(spot.x, spot.y, spot.z, this.random.nextFloat() * 360.0F, 0.0F);
                minion.finalizeSpawn(level, level.getCurrentDifficultyAt(minion.blockPosition()), MobSpawnType.MOB_SUMMONED, null, null);
                if (target != null) {
                    minion.setTarget(target);
                }
                if (level.addFreshEntity(minion)) {
                    this.minions.add(minion.getUUID());
                    RootSpikes.spawn(level, this, spot.x, spot.z, spot.y - 2, spot.y + 2, 0, 0.0F, 0, true);
                    level.sendParticles(ModParticles.SPORE.get(), spot.x, spot.y + 0.6, spot.z, 20, 0.4, 0.4, 0.4, 0.05);
                }
            }
        }
    }

    private void tickRoar(ServerLevel level, int t) {
        if (t == 1) {
            play(ModSounds.MYCELIARCH_ROAR.get(), 3.5F, 0.75F);
        }
        if (t == ROAR_HIT) {
            shove(level, 9.0, 1.0, 0.35, false);
            level.sendParticles(ModParticles.GLOW_SPORE.get(), getX(), getY() + 3.5, getZ(), 80, 2.0, 1.0, 2.0, 0.12);
            level.sendParticles(ModParticles.SPORE.get(), getX(), getY() + 2.0, getZ(), 60, 2.5, 1.5, 2.5, 0.1);
        }
        if (t > ROAR_HIT && t < 32 && t % 3 == 0) {
            ring(level, ModParticles.GLOW_SPORE.get(), this.position().add(0, 0.4, 0), 1.0 + (t - ROAR_HIT) * 0.45, 24);
        }
    }

    private void tickRain(ServerLevel level) {
        if (this.rainTicks <= 0) {
            return;
        }
        this.rainTicks--;
        LivingEntity target = getTarget();
        if (target == null || this.rainTicks % 4 != 0) {
            return;
        }
        boolean direct = this.rainTicks % 16 == 0;
        double x = target.getX() + (direct ? 0 : this.random.nextGaussian() * 2.6);
        double z = target.getZ() + (direct ? 0 : this.random.nextGaussian() * 2.6);
        double floor = RootSpikes.floor(level, x, z, target.getY() - 6, target.getY() + 4);
        double groundY = Double.isNaN(floor) ? target.getY() : floor;
        // Mark where it will land, then drop the glob from high above.
        level.sendParticles(ModParticles.GLOW_SPORE.get(), x, groundY + 0.15, z, 6, 0.25, 0.02, 0.25, 0.01);
        SporeGlobEntity glob = new SporeGlobEntity(level, x, groundY + 11.0, z);
        glob.setOwner(this);
        glob.setDamage(damage(3.0F));
        glob.setDeltaMovement(0.0, -0.55, 0.0);
        level.addFreshEntity(glob);
    }

    private List<LivingEntity> victims(Vec3 centre, double radius, double below, double above) {
        AABB box = new AABB(centre.x - radius, centre.y + below, centre.z - radius, centre.x + radius, centre.y + above, centre.z + radius);
        return this.level().getEntitiesOfClass(LivingEntity.class, box, e -> e != this && e.isAlive() && !e.isSpectator()
                && !e.getType().is(ModTags.Entities.FUNGAL) && e.position().subtract(centre).horizontalDistanceSqr() <= radius * radius
                && !(e instanceof Player p && p.isCreative()));
    }

    private void shove(ServerLevel level, double radius, double strength, double lift, boolean hurt) {
        for (LivingEntity e : victims(this.position(), radius, -2.0, 5.0)) {
            Vec3 away = e.position().subtract(this.position()).multiply(1, 0, 1);
            double d = Math.max(0.5, away.length());
            Vec3 push = away.normalize().scale(strength * (1.0 - d / (radius + 1.0)) + 0.3);
            e.push(push.x, lift, push.z);
            e.hurtMarked = true;
        }
    }

    private void ring(ServerLevel level, ParticleOptions particle, Vec3 centre, double radius, int count) {
        for (int i = 0; i < count; i++) {
            double a = (Math.PI * 2 * i) / count;
            level.sendParticles(particle, centre.x + Math.cos(a) * radius, centre.y + 0.15, centre.z + Math.sin(a) * radius,
                    1, 0.05, 0.02, 0.05, 0.0);
        }
    }

    private BlockState groundState() {
        BlockState below = this.level().getBlockState(this.blockPosition().below());
        return below.isAir() ? Blocks.ROOTED_DIRT.defaultBlockState() : below;
    }

    private void play(SoundEvent sound, float volume, float pitch) {
        this.level().playSound(null, getX(), getY(), getZ(), sound, SoundSource.HOSTILE, volume, pitch);
    }

    private int countMinions() {
        if (!(this.level() instanceof ServerLevel level)) {
            return 0;
        }
        this.minions.removeIf(id -> {
            Entity e = level.getEntity(id);
            return e == null || !e.isAlive();
        });
        return this.minions.size();
    }

    private void tickMinions(ServerLevel level) {
        if (this.tickCount % 40 == 0) {
            countMinions();
            LivingEntity target = getTarget();
            if (target != null) {
                for (UUID id : this.minions) {
                    if (level.getEntity(id) instanceof Mob mob && mob.getTarget() == null) {
                        mob.setTarget(target);
                    }
                }
            }
        }
    }

    // ---------------------------------------------------------------------------------------------- damage and death

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (isUntouchable() && !source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return false;
        }
        Entity attacker = source.getEntity();
        if (attacker == this || (attacker != null && attacker.getType().is(ModTags.Entities.FUNGAL))) {
            return false;
        }
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide && !isBloom() && this.isAlive() && this.getHealth() <= this.getMaxHealth() / 2) {
            secondBloom();
        }
        return hurt;
    }

    private void secondBloom() {
        this.entityData.set(DATA_BLOOM, true);
        applyBloomSpeed();
        this.bossEvent.setColor(BossEvent.BossBarColor.BLUE);
        this.rainCooldown = 40;
        this.rainTicks = 0;
        begin(ROAR, getTarget());
        announce("second_bloom", ChatFormatting.AQUA);
    }

    private void applyBloomSpeed() {
        AttributeInstance speed = this.getAttribute(Attributes.MOVEMENT_SPEED);
        if (speed != null) {
            speed.removeModifier(BLOOM_SPEED);
            speed.addTransientModifier(new AttributeModifier(BLOOM_SPEED, "spore_and_stem:second_bloom_speed", 0.3,
                    AttributeModifier.Operation.MULTIPLY_BASE));
        }
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        this.rainTicks = 0;
        this.bossEvent.setProgress(0.0F);
        getNavigation().stop();
    }

    /** Loot waits until the collapse is over (see tickDeath). */
    @Override
    protected void dropAllDeathLoot(DamageSource source) {
        this.pendingDeathSource = source;
    }

    /** Ticks since it began to collapse; on the client deathTime stays 0 so vanilla's red death tint is not drawn. */
    public int getCollapseTicks() {
        return this.level().isClientSide ? this.collapseTicks : this.deathTime;
    }

    @Override
    protected void tickDeath() {
        if (this.level().isClientSide) {
            this.collapseTicks++;
            return;
        }
        this.deathTime++;
        if (this.level() instanceof ServerLevel level) {
            if (this.deathTime == 1) {
                play(ModSounds.MYCELIARCH_ROAR.get(), 2.5F, 0.55F);
            }
            if (this.deathTime % 3 == 0) {
                double h = Math.max(0.5, 3.8 - this.deathTime * 0.06);
                level.sendParticles(ModParticles.SPORE.get(), getX(), getY() + h, getZ(), 18, 1.2, 0.8, 1.2, 0.06);
                level.sendParticles(ModParticles.GLOW_SPORE.get(), getX(), getY() + h, getZ(), 8, 1.4, 0.8, 1.4, 0.05);
            }
            if (this.deathTime == 30) {
                play(ModSounds.MYCELIARCH_SLAM.get(), 2.0F, 0.6F);
                level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, groundState()), getX(), getY() + 0.2, getZ(),
                        50, 1.4, 0.2, 1.4, 0.2);
            }
            if (this.deathTime == DEATH_TICKS - 5 && this.pendingDeathSource != null) {
                super.dropAllDeathLoot(this.pendingDeathSource);
                this.pendingDeathSource = null;
            }
            if (this.deathTime >= DEATH_TICKS && !this.isRemoved()) {
                level.sendParticles(ModParticles.SPORE.get(), getX(), getY() + 1.0, getZ(), 120, 1.8, 1.2, 1.8, 0.15);
                level.sendParticles(ModParticles.GLOW_SPORE.get(), getX(), getY() + 1.0, getZ(), 60, 1.8, 1.2, 1.8, 0.1);
                this.level().broadcastEntityEvent(this, (byte) 60);
                this.remove(RemovalReason.KILLED);
            }
        }
    }

    @Override
    protected boolean isAlwaysExperienceDropper() {
        return true;
    }

    // ---------------------------------------------------------------------------------------------- client

    @Override
    public void tick() {
        super.tick();
        if (this.level().isClientSide) {
            if (!this.idleState.isStarted()) {
                this.idleState.start(this.tickCount);
            }
            if (this.collapseTicks > 0 && !this.deathState.isStarted()) {
                this.deathState.start(this.tickCount);
            }
            if (this.isAlive() && !isEmerging() && this.random.nextInt(isBloom() ? 2 : 4) == 0) {
                // Luminous spores drift down from the gills.
                double a = this.random.nextDouble() * Math.PI * 2;
                double r = this.random.nextDouble() * 1.2;
                this.level().addParticle(ModParticles.GLOW_SPORE.get(), getX() + Math.cos(a) * r, getY() + 3.75,
                        getZ() + Math.sin(a) * r, 0.0, -0.015, 0.0);
            }
        }
    }

    // ---------------------------------------------------------------------------------------------- vanilla tweaks

    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        this.bossEvent.addPlayer(player);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        this.bossEvent.removePlayer(player);
    }

    @Override
    public void setCustomName(@Nullable Component name) {
        super.setCustomName(name);
        this.bossEvent.setName(this.getDisplayName());
    }

    @Override
    public boolean canBeAffected(MobEffectInstance effect) {
        MobEffect type = effect.getEffect();
        if (type == ModEffects.MYCOSIS.get() || type == ModEffects.ROOTED.get() || type == MobEffects.POISON
                || type == MobEffects.WITHER) {
            return false;
        }
        return super.canBeAffected(effect);
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean isPushedByFluid() {
        return false;
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public boolean canChangeDimensions() {
        return false;
    }

    @Override
    protected boolean canRide(Entity vehicle) {
        return false;
    }

    @Override
    public boolean isSensitiveToWater() {
        return false;
    }

    @Override
    protected float getSoundVolume() {
        return 2.0F;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 160;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return getState() == IDLE ? ModSounds.MYCELIARCH_AMBIENT.get() : null;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.MYCELIARCH_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.MYCELIARCH_DEATH.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        this.playSound(ModSounds.MYCELIARCH_STEP.get(), 1.2F, 0.85F + this.random.nextFloat() * 0.2F);
    }

    // ---------------------------------------------------------------------------------------------- saving

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putByte("State", getState());
        tag.putInt("StateTicks", this.stateTicks);
        tag.putBoolean("Bloom", isBloom());
        tag.putInt("RainTicks", this.rainTicks);
        tag.putIntArray("Cooldowns", new int[]{this.globalCooldown, this.slamCooldown, this.eruptCooldown, this.novaCooldown,
                this.broodCooldown, this.rainCooldown});
        if (this.home != null) {
            tag.put("Home", NbtUtils.writeBlockPos(this.home));
        }
        if (this.summoner != null) {
            tag.putUUID("Summoner", this.summoner);
        }
        ListTag list = new ListTag();
        for (UUID id : this.minions) {
            list.add(NbtUtils.createUUID(id));
        }
        tag.put("Minions", list);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        byte state = tag.getByte("State");
        this.entityData.set(DATA_STATE, state >= 0 && state < DURATION.length ? state : IDLE);
        this.stateTicks = tag.getInt("StateTicks");
        this.entityData.set(DATA_BLOOM, tag.getBoolean("Bloom"));
        this.rainTicks = tag.getInt("RainTicks");
        int[] cd = tag.getIntArray("Cooldowns");
        if (cd.length == 6) {
            this.globalCooldown = cd[0];
            this.slamCooldown = cd[1];
            this.eruptCooldown = cd[2];
            this.novaCooldown = cd[3];
            this.broodCooldown = cd[4];
            this.rainCooldown = cd[5];
        }
        if (tag.contains("Home", Tag.TAG_COMPOUND)) {
            this.home = NbtUtils.readBlockPos(tag.getCompound("Home"));
            this.restrictTo(this.home, (int) LEASH);
        }
        if (tag.hasUUID("Summoner")) {
            this.summoner = tag.getUUID("Summoner");
        }
        this.minions.clear();
        for (Tag t : tag.getList("Minions", Tag.TAG_INT_ARRAY)) {
            this.minions.add(NbtUtils.loadUUID(t));
        }
        if (isBloom()) {
            applyBloomSpeed();
            this.bossEvent.setColor(BossEvent.BossBarColor.BLUE);
        }
        this.bossEvent.setVisible(getState() != EMERGING || this.stateTicks >= RITUAL_TICKS);
        if (this.hasCustomName()) {
            this.bossEvent.setName(this.getDisplayName());
        }
    }

    /** Eye at 3.4 of 4.2 blocks (scaled with the body, so babies keep the proportion). */
    @Override
    protected float getStandingEyeHeight(Pose pose, EntityDimensions dimensions) {
        return dimensions.height * 0.8095F;
    }
}
