package com.nightbeam.sporeandstem.entity;

import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.Pose;
import com.nightbeam.sporeandstem.config.SporeConfig;
import com.nightbeam.sporeandstem.entity.ai.TendFungiGoal;
import com.nightbeam.sporeandstem.item.CrownOfTheBloomItem;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModItems;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowOwnerGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

/**
 * A little walking mushroom. Shy of players (unless they wear the Crown of the Bloom), it tends the small fungi around
 * it. Tame it with Truffles (one in three): it follows, sits on use, and now and then sheds a mushroom of its kind.
 * Four cap variants, chosen by biome.
 */
public class SporelingEntity extends TamableAnimal {
    public static final byte EVENT_SNEEZE = 101;
    public static final byte EVENT_HAPPY = 102;
    private static final EntityDataAccessor<Integer> DATA_VARIANT = SynchedEntityData.defineId(SporelingEntity.class,
            EntityDataSerializers.INT);

    public final AnimationState sneezeState = new AnimationState();
    public final AnimationState happyState = new AnimationState();
    private int shedTimer = -1;
    private int sneezeTicks;

    public SporelingEntity(EntityType<? extends SporelingEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return TamableAnimal.createMobAttributes().add(Attributes.MAX_HEALTH, 8.0).add(Attributes.MOVEMENT_SPEED, 0.25)
                .add(Attributes.FOLLOW_RANGE, 16.0);
    }

    /** Natural spawns: on dirt-like ground, mycelium or moss, in any light (they like the shade). */
    public static boolean checkSpawnRules(EntityType<SporelingEntity> type, LevelAccessor level, MobSpawnType spawnType,
                                          BlockPos pos, RandomSource random) {
        BlockState below = level.getBlockState(pos.below());
        return below.is(BlockTags.DIRT) || below.is(ModTags.Blocks.FUNGUS_SOIL);
    }

    public enum Variant {
        GLOWCAP("glowcap"), BOUNCECAP("bouncecap"), INKCAP("inkcap"), CHANTERELLE("chanterelle");

        private final String id;

        Variant(String id) {
            this.id = id;
        }

        public String id() {
            return id;
        }

        public Item item() {
            return switch (this) {
                case GLOWCAP -> ModItems.GLOWCAP.get();
                case BOUNCECAP -> ModItems.BOUNCECAP.get();
                case INKCAP -> ModItems.INKCAP.get();
                case CHANTERELLE -> ModItems.CHANTERELLE.get();
            };
        }

        public static Variant byId(int id) {
            Variant[] values = values();
            return values[Math.floorMod(id, values.length)];
        }
    }

    // ---- data ---------------------------------------------------------------------------------------------------

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_VARIANT, 0);
    }

    public Variant getVariant() {
        return Variant.byId(this.entityData.get(DATA_VARIANT));
    }

    public void setVariant(Variant variant) {
        this.entityData.set(DATA_VARIANT, variant.ordinal());
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putString("Variant", getVariant().id());
        tag.putInt("ShedTimer", shedTimer);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        for (Variant v : Variant.values()) {
            if (v.id().equals(tag.getString("Variant"))) {
                setVariant(v);
            }
        }
        if (tag.contains("ShedTimer")) {
            shedTimer = tag.getInt("ShedTimer");
        }
    }

    // ---- spawning -----------------------------------------------------------------------------------------------

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType spawnType,
                                        @Nullable SpawnGroupData groupData, @Nullable CompoundTag dataTag) {
        setVariant(variantFor(level.getBiome(this.blockPosition()), level.getRandom()));
        return super.finalizeSpawn(level, difficulty, spawnType, groupData, dataTag);
    }

    static Variant variantFor(Holder<Biome> biome, RandomSource random) {
        if (biome.is(Biomes.MUSHROOM_FIELDS) || biome.is(Biomes.LUSH_CAVES) || biome.is(Biomes.DRIPSTONE_CAVES)) {
            return Variant.GLOWCAP;
        }
        if (biome.is(Biomes.SWAMP) || biome.is(Biomes.MANGROVE_SWAMP) || biome.is(Biomes.DARK_FOREST)) {
            return Variant.INKCAP;
        }
        if (biome.is(BiomeTags.IS_TAIGA) || biome.is(Biomes.GROVE)) {
            return Variant.CHANTERELLE;
        }
        if (biome.is(Biomes.FLOWER_FOREST) || biome.is(Biomes.MEADOW) || biome.is(Biomes.CHERRY_GROVE)
                || biome.is(Biomes.BIRCH_FOREST) || biome.is(Biomes.OLD_GROWTH_BIRCH_FOREST)) {
            return Variant.BOUNCECAP;
        }
        return Variant.byId(random.nextInt(Variant.values().length));
    }

    // ---- goals --------------------------------------------------------------------------------------------------

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new PanicGoal(this, 1.4));
        this.goalSelector.addGoal(2, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(3, new AvoidEntityGoal<>(this, Player.class, 6.0F, 1.0, 1.3, this::scaredOf) {
            @Override
            public boolean canUse() {
                return !SporelingEntity.this.isTame() && super.canUse();
            }
        });
        this.goalSelector.addGoal(4, new BreedGoal(this, 1.0));
        this.goalSelector.addGoal(5, new TemptGoal(this, 1.0, Ingredient.of(ModItems.TRUFFLE.get()), false));
        this.goalSelector.addGoal(6, new FollowOwnerGoal(this, 1.0, 6.0F, 2.0F, false));
        this.goalSelector.addGoal(7, new TendFungiGoal(this));
        this.goalSelector.addGoal(8, new WaterAvoidingRandomStrollGoal(this, 0.8));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 6.0F));
        this.goalSelector.addGoal(10, new RandomLookAroundGoal(this));
    }

    private boolean scaredOf(LivingEntity entity) {
        if (!(entity instanceof Player player) || player.isCreative() || player.isSpectator()) {
            return false;
        }
        return !CrownOfTheBloomItem.isWorn(player) && !isFood(player.getMainHandItem()) && !isFood(player.getOffhandItem());
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return stack.is(ModItems.TRUFFLE.get());
    }

    // ---- interaction --------------------------------------------------------------------------------------------

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (this.level().isClientSide) {
            boolean handled = this.isOwnedBy(player) || (!this.isTame() && this.isFood(stack));
            return handled ? InteractionResult.CONSUME : InteractionResult.PASS;
        }
        if (!this.isTame()) {
            if (this.isFood(stack)) {
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
                if (this.random.nextInt(3) == 0) {
                    this.tame(player);
                    this.navigation.stop();
                    this.setTarget(null);
                    this.setOrderedToSit(true);
                    this.level().broadcastEntityEvent(this, (byte) 7);
                    celebrate();
                } else {
                    this.level().broadcastEntityEvent(this, (byte) 6);
                }
                return InteractionResult.SUCCESS;
            }
            return super.mobInteract(player, hand);
        }
        if (this.isOwnedBy(player)) {
            if (this.isFood(stack) && this.getHealth() < this.getMaxHealth()) {
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
                this.heal(4.0F);
                celebrate();
                return InteractionResult.SUCCESS;
            }
            InteractionResult result = super.mobInteract(player, hand);
            if (result.consumesAction()) {
                return result;
            }
            this.setOrderedToSit(!this.isOrderedToSit());
            this.jumping = false;
            this.navigation.stop();
            this.setTarget(null);
            return InteractionResult.SUCCESS;
        }
        return super.mobInteract(player, hand);
    }

    /** Hops and spins with joy (fed, tamed, or done tending a mushroom). */
    public void celebrate() {
        if (!this.level().isClientSide) {
            this.level().broadcastEntityEvent(this, EVENT_HAPPY);
            this.playSound(ModSounds.SPORELING_HAPPY.get(), 0.7F, this.getVoicePitch());
        }
    }

    public void sneeze() {
        if (!this.level().isClientSide && sneezeTicks <= 0) {
            this.level().broadcastEntityEvent(this, EVENT_SNEEZE);
            this.playSound(ModSounds.SPORELING_SNEEZE.get(), 0.7F, this.getVoicePitch());
            sneezeTicks = 13;
        }
    }

    // ---- ticking ------------------------------------------------------------------------------------------------

    @Override
    public void aiStep() {
        super.aiStep();
        if (this.level() instanceof ServerLevel level) {
            if (sneezeTicks > 0 && --sneezeTicks == 0) {
                // The "choo": a puff of spores from under the cap.
                double yaw = Math.toRadians(this.yBodyRot);
                level.sendParticles(getVariant() == Variant.GLOWCAP ? ModParticles.GLOW_SPORE.get() : ModParticles.SPORE.get(),
                        this.getX() - Math.sin(yaw) * 0.35, this.getY() + 0.35, this.getZ() + Math.cos(yaw) * 0.35,
                        10, 0.12, 0.08, 0.12, 0.03);
            }
            if (!this.isInSittingPose() && this.random.nextInt(1600) == 0) {
                sneeze();
            }
            if (this.isTame() && this.isAlive()) {
                if (shedTimer < 0) {
                    shedTimer = nextShed();
                } else if (--shedTimer == 0) {
                    this.spawnAtLocation(new ItemStack(getVariant().item()));
                    sneeze();
                    shedTimer = nextShed();
                }
            }
        }
    }

    private int nextShed() {
        SporeConfig config = SporeConfig.get();
        int min = config.sporelingShedMin * 1200;
        int max = Math.max(min + 1, config.sporelingShedMax * 1200);
        return min + this.random.nextInt(max - min);
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == EVENT_SNEEZE) {
            sneezeState.start(this.tickCount);
        } else if (id == EVENT_HAPPY) {
            happyState.start(this.tickCount);
        } else {
            super.handleEntityEvent(id);
        }
    }

    // ---- breeding, loot, sounds ---------------------------------------------------------------------------------

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        SporelingEntity child = ModEntities.SPORELING.get().create(level);
        if (child != null) {
            Variant variant = this.random.nextBoolean() || !(partner instanceof SporelingEntity other)
                    ? this.getVariant() : other.getVariant();
            child.setVariant(variant);
            if (this.isTame() && this.getOwnerUUID() != null) {
                child.setOwnerUUID(this.getOwnerUUID());
                child.setTame(true);
            }
        }
        return child;
    }

    @Override
    protected void dropCustomDeathLoot(DamageSource source, int looting, boolean recentlyHit) {
        super.dropCustomDeathLoot(source, looting, recentlyHit);
        this.spawnAtLocation(new ItemStack(getVariant().item()));
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.SPORELING_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.SPORELING_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.SPORELING_DEATH.get();
    }

    @Override
    protected float getSoundVolume() {
        return 0.6F;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }

    /** Eye at 0.35 of 0.7 blocks (scaled with the body, so babies keep the proportion). */
    @Override
    protected float getStandingEyeHeight(Pose pose, EntityDimensions dimensions) {
        return dimensions.height * 0.5000F;
    }
}
