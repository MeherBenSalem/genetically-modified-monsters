package com.nightbeam.sporeandstem.dev;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.platform.Services;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.level.block.state.properties.Property;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.BiConsumer;

/**
 * Development only: writes every registered id of this mod (with block state properties, description ids and loot
 * table ids) to {@code spore_and_stem_registry.json} in the game directory. tools/assets/check.py validates the
 * generated resources against it.
 */
public final class RegistryDump {

    private RegistryDump() {
    }

    public static void writeIfDevelopment() {
        if (!Services.PLATFORM.isDevelopmentEnvironment()) {
            return;
        }
        Path file = Services.PLATFORM.getConfigDirectory().toAbsolutePath().getParent().resolve(SporeAndStem.MOD_ID + "_registry.json");
        try {
            Files.writeString(file, new GsonBuilder().setPrettyPrinting().create().toJson(dump()), StandardCharsets.UTF_8);
            SporeAndStem.LOGGER.info("Wrote registry dump to {}", file);
        } catch (Exception e) {
            SporeAndStem.LOGGER.warn("Could not write registry dump", e);
        }
    }

    private static JsonObject dump() {
        JsonObject root = new JsonObject();
        root.addProperty("platform", Services.PLATFORM.getPlatformName());
        JsonArray blocks = new JsonArray();
        each(BuiltInRegistries.BLOCK, (id, block) -> {
            JsonObject o = new JsonObject();
            o.addProperty("id", id.getPath());
            o.addProperty("class", block.getClass().getName());
            o.addProperty("description", block.getDescriptionId());
            o.addProperty("loot_table", block.getLootTable().location().toString());
            o.addProperty("has_item", block.asItem() != net.minecraft.world.item.Items.AIR);
            JsonObject props = new JsonObject();
            for (Property<?> property : block.getStateDefinition().getProperties()) {
                JsonArray values = new JsonArray();
                property.getPossibleValues().forEach(v -> values.add(name(property, v)));
                props.add(property.getName(), values);
            }
            o.add("properties", props);
            blocks.add(o);
        });
        root.add("blocks", blocks);
        JsonArray items = new JsonArray();
        each(BuiltInRegistries.ITEM, (id, item) -> {
            JsonObject o = new JsonObject();
            o.addProperty("id", id.getPath());
            o.addProperty("class", item.getClass().getName());
            o.addProperty("description", item.getDescriptionId());
            if (item instanceof BlockItem blockItem) {
                o.addProperty("block", BuiltInRegistries.BLOCK.getKey(blockItem.getBlock()).toString());
            }
            items.add(o);
        });
        root.add("items", items);
        JsonArray entities = new JsonArray();
        each(BuiltInRegistries.ENTITY_TYPE, (id, type) -> {
            JsonObject o = new JsonObject();
            o.addProperty("id", id.getPath());
            o.addProperty("description", type.getDescriptionId());
            o.addProperty("category", type.getCategory().getName());
            o.addProperty("living", type.getCategory() != MobCategory.MISC);
            o.addProperty("loot_table", type.getDefaultLootTable().location().toString());
            entities.add(o);
        });
        root.add("entity_types", entities);
        root.add("sound_events", ids(BuiltInRegistries.SOUND_EVENT));
        root.add("mob_effects", ids(BuiltInRegistries.MOB_EFFECT));
        root.add("particle_types", ids(BuiltInRegistries.PARTICLE_TYPE));
        root.add("features", ids(BuiltInRegistries.FEATURE));
        root.add("armor_materials", ids(BuiltInRegistries.ARMOR_MATERIAL));
        JsonArray tags = new JsonArray();
        for (Class<?> holder : ModTags.class.getDeclaredClasses()) {
            for (Field field : holder.getDeclaredFields()) {
                if (Modifier.isStatic(field.getModifiers()) && TagKey.class.isAssignableFrom(field.getType())) {
                    try {
                        TagKey<?> key = (TagKey<?>) field.get(null);
                        JsonObject o = new JsonObject();
                        o.addProperty("registry", key.registry().location().getPath());
                        o.addProperty("id", key.location().toString());
                        tags.add(o);
                    } catch (IllegalAccessException ignored) {
                    }
                }
            }
        }
        root.add("tags", tags);
        return root;
    }

    @SuppressWarnings("unchecked")
    private static <T extends Comparable<T>> String name(Property<?> property, Object value) {
        return ((Property<T>) property).getName((T) value);
    }

    private static <T> void each(Registry<T> registry, BiConsumer<ResourceLocation, T> sink) {
        registry.keySet().stream().filter(id -> id.getNamespace().equals(SporeAndStem.MOD_ID)).sorted()
                .forEach(id -> sink.accept(id, registry.get(id)));
    }

    private static <T> JsonArray ids(Registry<T> registry) {
        JsonArray array = new JsonArray();
        registry.keySet().stream().filter(id -> id.getNamespace().equals(SporeAndStem.MOD_ID)).sorted()
                .forEach(id -> array.add(id.getPath()));
        return array;
    }
}
