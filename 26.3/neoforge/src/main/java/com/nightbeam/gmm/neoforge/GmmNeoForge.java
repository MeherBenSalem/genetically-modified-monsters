package com.nightbeam.gmm.neoforge;

import com.nightbeam.gmm.Gmm;
import com.nightbeam.gmm.entity.AdaptiveCreeperEntity;
import com.nightbeam.gmm.entity.ClimbCreeperEntity;
import com.nightbeam.gmm.entity.HunterCreeperEntity;
import com.nightbeam.gmm.entity.LeapCreeperEntity;
import com.nightbeam.gmm.entity.OverchargeCreeperEntity;
import com.nightbeam.gmm.entity.SilentCreeperEntity;
import com.nightbeam.gmm.entity.SwiftCreeperEntity;
import com.nightbeam.gmm.neoforge.client.GmmNeoForgeClient;
import com.nightbeam.gmm.registry.ModEntities;
import com.nightbeam.gmm.registry.ModItems;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

@Mod(Gmm.MOD_ID)
public class GmmNeoForge {
    private static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(BuiltInRegistries.ENTITY_TYPE, Gmm.MOD_ID);
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(BuiltInRegistries.ITEM, Gmm.MOD_ID);
    private static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Gmm.MOD_ID);

    public GmmNeoForge(IEventBus modBus) {
        registerContent();
        TABS.register("main", () -> CreativeModeTab.builder()
                .title(Component.translatable("itemGroup.gmm"))
                .icon(() -> new ItemStack(ModItems.LEAP_CREEPER_SPAWN_EGG.get()))
                .displayItems((parameters, tabData) -> {
                    tabData.accept(ModItems.LEAP_CREEPER_SPAWN_EGG.get());
                    tabData.accept(ModItems.CLIMB_CREEPER_SPAWN_EGG.get());
                    tabData.accept(ModItems.SWIFT_CREEPER_SPAWN_EGG.get());
                    tabData.accept(ModItems.ADAPTIVE_CREEPER_SPAWN_EGG.get());
                    tabData.accept(ModItems.OVERCHARGE_CREEPER_SPAWN_EGG.get());
                    tabData.accept(ModItems.SILENT_CREEPER_SPAWN_EGG.get());
                    tabData.accept(ModItems.HUNTER_CREEPER_SPAWN_EGG.get());
                })
                .build());
        ENTITIES.register(modBus);
        ITEMS.register(modBus);
        TABS.register(modBus);
        modBus.addListener(this::attributes);
        modBus.addListener(GmmNeoForgeClient::registerRenderers);
    }

    private static void registerContent() {
        DeferredHolder<EntityType<?>, EntityType<LeapCreeperEntity>> leap = registerEntity("leap_creeper",
                EntityType.Builder.<LeapCreeperEntity>of(LeapCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.LEAP_CREEPER = leap;
        DeferredHolder<EntityType<?>, EntityType<ClimbCreeperEntity>> climb = registerEntity("climb_creeper",
                EntityType.Builder.<ClimbCreeperEntity>of(ClimbCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.CLIMB_CREEPER = climb;
        DeferredHolder<EntityType<?>, EntityType<SwiftCreeperEntity>> swift = registerEntity("swift_creeper",
                EntityType.Builder.<SwiftCreeperEntity>of(SwiftCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.SWIFT_CREEPER = swift;
        DeferredHolder<EntityType<?>, EntityType<AdaptiveCreeperEntity>> adaptive = registerEntity("adaptive_creeper",
                EntityType.Builder.<AdaptiveCreeperEntity>of(AdaptiveCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.ADAPTIVE_CREEPER = adaptive;
        DeferredHolder<EntityType<?>, EntityType<OverchargeCreeperEntity>> overcharge = registerEntity("overcharge_creeper",
                EntityType.Builder.<OverchargeCreeperEntity>of(OverchargeCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.OVERCHARGE_CREEPER = overcharge;
        DeferredHolder<EntityType<?>, EntityType<SilentCreeperEntity>> silent = registerEntity("silent_creeper",
                EntityType.Builder.<SilentCreeperEntity>of(SilentCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.SILENT_CREEPER = silent;
        DeferredHolder<EntityType<?>, EntityType<HunterCreeperEntity>> hunter = registerEntity("hunter_creeper",
                EntityType.Builder.<HunterCreeperEntity>of(HunterCreeperEntity::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.HUNTER_CREEPER = hunter;
        ModItems.LEAP_CREEPER_SPAWN_EGG = ITEMS.register("leap_creeper_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.LEAP_CREEPER.get())));
        ModItems.CLIMB_CREEPER_SPAWN_EGG = ITEMS.register("climb_creeper_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.CLIMB_CREEPER.get())));
        ModItems.SWIFT_CREEPER_SPAWN_EGG = ITEMS.register("swift_creeper_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.SWIFT_CREEPER.get())));
        ModItems.ADAPTIVE_CREEPER_SPAWN_EGG = ITEMS.register("adaptive_creeper_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.ADAPTIVE_CREEPER.get())));
        ModItems.OVERCHARGE_CREEPER_SPAWN_EGG = ITEMS.register("overcharge_creeper_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.OVERCHARGE_CREEPER.get())));
        ModItems.SILENT_CREEPER_SPAWN_EGG = ITEMS.register("silent_creeper_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.SILENT_CREEPER.get())));
        ModItems.HUNTER_CREEPER_SPAWN_EGG = ITEMS.register("hunter_creeper_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.HUNTER_CREEPER.get())));
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

    private static <T extends net.minecraft.world.entity.Entity> DeferredHolder<EntityType<?>, EntityType<T>> registerEntity(String name, EntityType.Builder<T> builder) {
        ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, Identifier.fromNamespaceAndPath(Gmm.MOD_ID, name));
        return ENTITIES.register(name, () -> builder.build(key));
    }
}
