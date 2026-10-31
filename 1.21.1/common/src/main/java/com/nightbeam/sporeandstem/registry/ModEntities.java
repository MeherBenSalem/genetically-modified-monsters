package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.entity.BloatshroomEntity;
import com.nightbeam.sporeandstem.entity.GlowmothEntity;
import com.nightbeam.sporeandstem.entity.MimicapEntity;
import com.nightbeam.sporeandstem.entity.MyceliarchEntity;
import com.nightbeam.sporeandstem.entity.RootSpikeEntity;
import com.nightbeam.sporeandstem.entity.ShamblerEntity;
import com.nightbeam.sporeandstem.entity.SporelingEntity;
import com.nightbeam.sporeandstem.entity.SporemawEntity;
import com.nightbeam.sporeandstem.entity.TrufflerEntity;
import com.nightbeam.sporeandstem.entity.projectile.SporeBombEntity;
import com.nightbeam.sporeandstem.entity.projectile.SporeGlobEntity;
import com.nightbeam.sporeandstem.platform.Services;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementType;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;

import java.util.function.BiConsumer;

/**
 * Entity types. Loaders call {@link #registerAttributes} and {@link #registerSpawnPlacements}; renderers are wired
 * in the client package.
 */
public final class ModEntities {
    public static final RegistryEntry<EntityType<SporelingEntity>> SPORELING = register("sporeling",
            EntityType.Builder.of(SporelingEntity::new, MobCategory.CREATURE).sized(0.55F, 0.7F).eyeHeight(0.35F).clientTrackingRange(8));
    public static final RegistryEntry<EntityType<BloatshroomEntity>> BLOATSHROOM = register("bloatshroom",
            EntityType.Builder.of(BloatshroomEntity::new, MobCategory.MONSTER).sized(0.8F, 1.0F).eyeHeight(0.7F).clientTrackingRange(8));
    public static final RegistryEntry<EntityType<ShamblerEntity>> SHAMBLER = register("shambler",
            EntityType.Builder.of(ShamblerEntity::new, MobCategory.MONSTER).sized(0.7F, 2.1F).eyeHeight(1.8F).clientTrackingRange(8));
    public static final RegistryEntry<EntityType<SporemawEntity>> SPOREMAW = register("sporemaw",
            EntityType.Builder.of(SporemawEntity::new, MobCategory.MONSTER).sized(0.9F, 1.3F).eyeHeight(1.0F).clientTrackingRange(8));
    public static final RegistryEntry<EntityType<MimicapEntity>> MIMICAP = register("mimicap",
            EntityType.Builder.of(MimicapEntity::new, MobCategory.MONSTER).sized(1.0F, 0.9F).eyeHeight(0.6F).clientTrackingRange(8));
    public static final RegistryEntry<EntityType<GlowmothEntity>> GLOWMOTH = register("glowmoth",
            EntityType.Builder.of(GlowmothEntity::new, MobCategory.AMBIENT).sized(0.5F, 0.4F).eyeHeight(0.2F).clientTrackingRange(5));
    public static final RegistryEntry<EntityType<TrufflerEntity>> TRUFFLER = register("truffler",
            EntityType.Builder.of(TrufflerEntity::new, MobCategory.CREATURE).sized(0.9F, 0.9F).eyeHeight(0.6F).clientTrackingRange(10));
    public static final RegistryEntry<EntityType<MyceliarchEntity>> MYCELIARCH = register("myceliarch",
            EntityType.Builder.of(MyceliarchEntity::new, MobCategory.MONSTER).sized(2.0F, 4.2F).eyeHeight(3.4F)
                    .fireImmune().clientTrackingRange(10));

    public static final RegistryEntry<EntityType<RootSpikeEntity>> ROOT_SPIKE = register("root_spike",
            EntityType.Builder.<RootSpikeEntity>of(RootSpikeEntity::new, MobCategory.MISC).sized(0.8F, 1.2F)
                    .clientTrackingRange(6).updateInterval(2));
    public static final RegistryEntry<EntityType<SporeGlobEntity>> SPORE_GLOB = register("spore_glob",
            EntityType.Builder.<SporeGlobEntity>of(SporeGlobEntity::new, MobCategory.MISC).sized(0.3F, 0.3F)
                    .clientTrackingRange(4).updateInterval(10));
    public static final RegistryEntry<EntityType<SporeBombEntity>> SPORE_BOMB = register("spore_bomb",
            EntityType.Builder.<SporeBombEntity>of(SporeBombEntity::new, MobCategory.MISC).sized(0.25F, 0.25F)
                    .clientTrackingRange(4).updateInterval(10));

    private ModEntities() {
    }

    private static <T extends Entity> RegistryEntry<EntityType<T>> register(String name, EntityType.Builder<T> builder) {
        return Services.REGISTRAR.register(Registries.ENTITY_TYPE, name, () -> builder.build(name));
    }

    public static void init() {
    }

    /** Default attributes for every living entity type. */
    public static void registerAttributes(BiConsumer<EntityType<? extends LivingEntity>, AttributeSupplier.Builder> sink) {
        sink.accept(SPORELING.get(), SporelingEntity.createAttributes());
        sink.accept(BLOATSHROOM.get(), BloatshroomEntity.createAttributes());
        sink.accept(SHAMBLER.get(), ShamblerEntity.createAttributes());
        sink.accept(SPOREMAW.get(), SporemawEntity.createAttributes());
        sink.accept(MIMICAP.get(), MimicapEntity.createAttributes());
        sink.accept(GLOWMOTH.get(), GlowmothEntity.createAttributes());
        sink.accept(TRUFFLER.get(), TrufflerEntity.createAttributes());
        sink.accept(MYCELIARCH.get(), MyceliarchEntity.createAttributes());
    }

    /**
     * Natural spawn rules. Fabric registers them through an access widener, NeoForge through its event. The Myceliarch
     * never spawns naturally (it is summoned), so it has none.
     */
    public static void registerSpawnPlacements(SpawnPlacementSink sink) {
        sink.register(SPORELING.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                SporelingEntity::checkSpawnRules);
        sink.register(TRUFFLER.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                TrufflerEntity::checkSpawnRules);
        sink.register(GLOWMOTH.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                GlowmothEntity::checkSpawnRules);
        sink.register(BLOATSHROOM.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkMonsterSpawnRules);
        sink.register(SHAMBLER.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkMonsterSpawnRules);
        sink.register(SPOREMAW.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkMonsterSpawnRules);
        // Mimicaps hide in plain sight: they spawn in any light.
        sink.register(MIMICAP.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                Monster::checkAnyLightMonsterSpawnRules);
    }

    @FunctionalInterface
    public interface SpawnPlacementSink {
        <T extends Mob> void register(EntityType<T> type, SpawnPlacementType placement, Heightmap.Types heightmap,
                                      SpawnPlacements.SpawnPredicate<T> predicate);
    }
}
