package com.nightbeam.gmm.fabric;

import com.nightbeam.gmm.Gmm;
import com.nightbeam.gmm.entity.LeapCreeperEntity;
import com.nightbeam.gmm.entity.ClimbCreeperEntity;
import com.nightbeam.gmm.entity.SwiftCreeperEntity;
import com.nightbeam.gmm.entity.AdaptiveCreeperEntity;
import com.nightbeam.gmm.entity.OverchargeCreeperEntity;
import com.nightbeam.gmm.entity.SilentCreeperEntity;
import com.nightbeam.gmm.entity.HunterCreeperEntity;
import com.nightbeam.gmm.registry.ModEntities;
import com.nightbeam.gmm.registry.ModItems;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;

import java.util.function.Supplier;

public class GmmFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        registerContent();
        FabricDefaultAttributeRegistry.register(ModEntities.LEAP_CREEPER.get(), LeapCreeperEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(ModEntities.CLIMB_CREEPER.get(), ClimbCreeperEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(ModEntities.SWIFT_CREEPER.get(), SwiftCreeperEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(ModEntities.ADAPTIVE_CREEPER.get(), AdaptiveCreeperEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(ModEntities.OVERCHARGE_CREEPER.get(), OverchargeCreeperEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(ModEntities.SILENT_CREEPER.get(), SilentCreeperEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(ModEntities.HUNTER_CREEPER.get(), HunterCreeperEntity.createAttributes());
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.LEAP_CREEPER.get(), 4, 1, 2);
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.CLIMB_CREEPER.get(), 4, 1, 2);
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.SWIFT_CREEPER.get(), 4, 1, 2);
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.ADAPTIVE_CREEPER.get(), 4, 1, 2);
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.OVERCHARGE_CREEPER.get(), 4, 1, 2);
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.SILENT_CREEPER.get(), 4, 1, 2);
        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.HUNTER_CREEPER.get(), 4, 1, 2);
    }

    private static void registerContent() {
        ModEntities.LEAP_CREEPER = entity("leap_creeper", EntityType.Builder.<LeapCreeperEntity>of(LeapCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.CLIMB_CREEPER = entity("climb_creeper", EntityType.Builder.<ClimbCreeperEntity>of(ClimbCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.SWIFT_CREEPER = entity("swift_creeper", EntityType.Builder.<SwiftCreeperEntity>of(SwiftCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.ADAPTIVE_CREEPER = entity("adaptive_creeper", EntityType.Builder.<AdaptiveCreeperEntity>of(AdaptiveCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.OVERCHARGE_CREEPER = entity("overcharge_creeper", EntityType.Builder.<OverchargeCreeperEntity>of(OverchargeCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.SILENT_CREEPER = entity("silent_creeper", EntityType.Builder.<SilentCreeperEntity>of(SilentCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.HUNTER_CREEPER = entity("hunter_creeper", EntityType.Builder.<HunterCreeperEntity>of(HunterCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModItems.LEAP_CREEPER_SPAWN_EGG = item("leap_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.LEAP_CREEPER.get(), 11141120, 16729156, new Item.Properties()));
        ModItems.CLIMB_CREEPER_SPAWN_EGG = item("climb_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.CLIMB_CREEPER.get(), 8912896, 13378082, new Item.Properties()));
        ModItems.SWIFT_CREEPER_SPAWN_EGG = item("swift_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.SWIFT_CREEPER.get(), 12259584, 16737843, new Item.Properties()));
        ModItems.ADAPTIVE_CREEPER_SPAWN_EGG = item("adaptive_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.ADAPTIVE_CREEPER.get(), 10027008, 14505216, new Item.Properties()));
        ModItems.OVERCHARGE_CREEPER_SPAWN_EGG = item("overcharge_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.OVERCHARGE_CREEPER.get(), 13369344, 16755200, new Item.Properties()));
        ModItems.SILENT_CREEPER_SPAWN_EGG = item("silent_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.SILENT_CREEPER.get(), 6684672, 2228224, new Item.Properties()));
        ModItems.HUNTER_CREEPER_SPAWN_EGG = item("hunter_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.HUNTER_CREEPER.get(), 11141154, 16711782, new Item.Properties()));
        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.SPAWN_EGGS).register(entries -> {
            entries.accept(ModItems.LEAP_CREEPER_SPAWN_EGG.get());
            entries.accept(ModItems.CLIMB_CREEPER_SPAWN_EGG.get());
            entries.accept(ModItems.SWIFT_CREEPER_SPAWN_EGG.get());
            entries.accept(ModItems.ADAPTIVE_CREEPER_SPAWN_EGG.get());
            entries.accept(ModItems.OVERCHARGE_CREEPER_SPAWN_EGG.get());
            entries.accept(ModItems.SILENT_CREEPER_SPAWN_EGG.get());
            entries.accept(ModItems.HUNTER_CREEPER_SPAWN_EGG.get());
        });
    }

    private static <T extends Item> Supplier<T> item(String name, Supplier<T> factory) {
        return register(name, () -> Registry.register(BuiltInRegistries.ITEM, id(name), factory.get()));
    }

    private static <T extends net.minecraft.world.entity.Entity> Supplier<EntityType<T>> entity(String name, EntityType.Builder<T> builder) {
        return register(name, () -> Registry.register(BuiltInRegistries.ENTITY_TYPE, id(name), builder.build(name)));
    }

    private static <T> Supplier<T> register(String name, Supplier<T> supplier) {
        T value = supplier.get();
        return () -> value;
    }

    private static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(Gmm.MOD_ID, path);
    }
}
