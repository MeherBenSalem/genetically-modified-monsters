package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.SporeAndStem;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;

import java.util.function.Supplier;

/**
 * Since 1.21.2 items, blocks and entity types must know their registry key when they are constructed. The
 * registration helpers wrap each factory in {@link #building}, so the property helpers here can stamp the key of the
 * entry being built, whenever the loader runs the factory.
 */
public final class Keys {
    private static final ThreadLocal<String> BUILDING = new ThreadLocal<>();

    private Keys() {
    }

    /** Runs {@code factory} with {@code name} as the entry being built. */
    public static <T> Supplier<T> building(String name, Supplier<T> factory) {
        return () -> {
            String outer = BUILDING.get();
            BUILDING.set(name);
            try {
                return factory.get();
            } finally {
                BUILDING.set(outer);
            }
        };
    }

    private static String current() {
        String name = BUILDING.get();
        if (name == null) {
            throw new IllegalStateException("No registry entry is being built");
        }
        return name;
    }

    /** Item properties carrying the key of the item being built. */
    public static Item.Properties itemProps() {
        return new Item.Properties().setId(item(current()));
    }

    /** Block properties carrying the key of the block being built. */
    public static BlockBehaviour.Properties blockProps() {
        return BlockBehaviour.Properties.of().setId(block(current()));
    }

    /** A full copy of another block's properties, re-keyed to the block being built. */
    public static BlockBehaviour.Properties copyOf(Block block) {
        return BlockBehaviour.Properties.ofFullCopy(block).setId(block(current()));
    }

    public static ResourceKey<Item> item(String name) {
        return ResourceKey.create(Registries.ITEM, SporeAndStem.id(name));
    }

    public static ResourceKey<Block> block(String name) {
        return ResourceKey.create(Registries.BLOCK, SporeAndStem.id(name));
    }

    public static ResourceKey<EntityType<?>> entity(String name) {
        return ResourceKey.create(Registries.ENTITY_TYPE, SporeAndStem.id(name));
    }
}
