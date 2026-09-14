package com.nightbeam.gmm.neoforge;

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
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

@Mod(Gmm.MOD_ID)
public class GmmNeoForge {
    private static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(BuiltInRegistries.ENTITY_TYPE, Gmm.MOD_ID);
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(BuiltInRegistries.ITEM, Gmm.MOD_ID);

    public GmmNeoForge(IEventBus modBus) {
        registerContent();
        ENTITIES.register(modBus);
        ITEMS.register(modBus);
        modBus.addListener(this::attributes);
        modBus.addListener(this::creativeTabs);
    }

    private static void registerContent() {
        DeferredHolder<EntityType<?>, EntityType<LeapCreeperEntity>> leap = ENTITIES.register("leap_creeper",
                () -> EntityType.Builder.<LeapCreeperEntity>of(LeapCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("leap_creeper"));
        ModEntities.LEAP_CREEPER = leap;
        DeferredHolder<EntityType<?>, EntityType<ClimbCreeperEntity>> climb = ENTITIES.register("climb_creeper",
                () -> EntityType.Builder.<ClimbCreeperEntity>of(ClimbCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("climb_creeper"));
        ModEntities.CLIMB_CREEPER = climb;
        DeferredHolder<EntityType<?>, EntityType<SwiftCreeperEntity>> swift = ENTITIES.register("swift_creeper",
                () -> EntityType.Builder.<SwiftCreeperEntity>of(SwiftCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("swift_creeper"));
        ModEntities.SWIFT_CREEPER = swift;
        DeferredHolder<EntityType<?>, EntityType<AdaptiveCreeperEntity>> adaptive = ENTITIES.register("adaptive_creeper",
                () -> EntityType.Builder.<AdaptiveCreeperEntity>of(AdaptiveCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("adaptive_creeper"));
        ModEntities.ADAPTIVE_CREEPER = adaptive;
        DeferredHolder<EntityType<?>, EntityType<OverchargeCreeperEntity>> overcharge = ENTITIES.register("overcharge_creeper",
                () -> EntityType.Builder.<OverchargeCreeperEntity>of(OverchargeCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("overcharge_creeper"));
        ModEntities.OVERCHARGE_CREEPER = overcharge;
        DeferredHolder<EntityType<?>, EntityType<SilentCreeperEntity>> silent = ENTITIES.register("silent_creeper",
                () -> EntityType.Builder.<SilentCreeperEntity>of(SilentCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("silent_creeper"));
        ModEntities.SILENT_CREEPER = silent;
        DeferredHolder<EntityType<?>, EntityType<HunterCreeperEntity>> hunter = ENTITIES.register("hunter_creeper",
                () -> EntityType.Builder.<HunterCreeperEntity>of(HunterCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("hunter_creeper"));
        ModEntities.HUNTER_CREEPER = hunter;
        ModItems.LEAP_CREEPER_SPAWN_EGG = ITEMS.register("leap_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.LEAP_CREEPER.get(), 11141120, 16729156, new Item.Properties()));
        ModItems.CLIMB_CREEPER_SPAWN_EGG = ITEMS.register("climb_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.CLIMB_CREEPER.get(), 8912896, 13378082, new Item.Properties()));
        ModItems.SWIFT_CREEPER_SPAWN_EGG = ITEMS.register("swift_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.SWIFT_CREEPER.get(), 12259584, 16737843, new Item.Properties()));
        ModItems.ADAPTIVE_CREEPER_SPAWN_EGG = ITEMS.register("adaptive_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.ADAPTIVE_CREEPER.get(), 10027008, 14505216, new Item.Properties()));
        ModItems.OVERCHARGE_CREEPER_SPAWN_EGG = ITEMS.register("overcharge_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.OVERCHARGE_CREEPER.get(), 13369344, 16755200, new Item.Properties()));
        ModItems.SILENT_CREEPER_SPAWN_EGG = ITEMS.register("silent_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.SILENT_CREEPER.get(), 6684672, 2228224, new Item.Properties()));
        ModItems.HUNTER_CREEPER_SPAWN_EGG = ITEMS.register("hunter_creeper_spawn_egg", () -> new SpawnEggItem(ModEntities.HUNTER_CREEPER.get(), 11141154, 16711782, new Item.Properties()));
    }

    private void attributes(EntityAttributeCreationEvent event) {
        event.put(ModEntities.LEAP_CREEPER.get(), LeapCreeperEntity.createAttributes().build());
        event.put(ModEntities.CLIMB_CREEPER.get(), ClimbCreeperEntity.createAttributes().build());
        event.put(ModEntities.SWIFT_CREEPER.get(), SwiftCreeperEntity.createAttributes().build());
        event.put(ModEntities.ADAPTIVE_CREEPER.get(), AdaptiveCreeperEntity.createAttributes().build());
        event.put(ModEntities.OVERCHARGE_CREEPER.get(), OverchargeCreeperEntity.createAttributes().build());
        event.put(ModEntities.SILENT_CREEPER.get(), SilentCreeperEntity.createAttributes().build());
        event.put(ModEntities.HUNTER_CREEPER.get(), HunterCreeperEntity.createAttributes().build());
    }

    private void creativeTabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.SPAWN_EGGS) {
            event.accept(ModItems.LEAP_CREEPER_SPAWN_EGG.get());
            event.accept(ModItems.CLIMB_CREEPER_SPAWN_EGG.get());
            event.accept(ModItems.SWIFT_CREEPER_SPAWN_EGG.get());
            event.accept(ModItems.ADAPTIVE_CREEPER_SPAWN_EGG.get());
            event.accept(ModItems.OVERCHARGE_CREEPER_SPAWN_EGG.get());
            event.accept(ModItems.SILENT_CREEPER_SPAWN_EGG.get());
            event.accept(ModItems.HUNTER_CREEPER_SPAWN_EGG.get());
        }
    }
}
