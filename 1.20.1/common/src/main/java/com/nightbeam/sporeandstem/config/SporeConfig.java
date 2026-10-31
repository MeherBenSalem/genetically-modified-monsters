package com.nightbeam.sporeandstem.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.platform.Services;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * {@code config/spore_and_stem.json}. Created on first launch with a {@code _comment} beside every key; missing keys
 * are added and your values are kept.
 */
public final class SporeConfig {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
    private static SporeConfig instance = new SporeConfig();

    public boolean mycosisEnabled = true;
    public boolean mycosisRising = true;
    public int mycosisDamageInterval = 80;
    public double myceliarchHealth = 300.0;
    public double myceliarchDamageMultiplier = 1.0;
    public int sporelingShedMin = 5;
    public int sporelingShedMax = 10;
    public double trufflerDigChance = 0.15;

    public static SporeConfig get() {
        return instance;
    }

    public static void load() {
        Path path = Services.PLATFORM.getConfigDirectory().resolve(SporeAndStem.MOD_ID + ".json");
        SporeConfig config = new SporeConfig();
        try {
            if (Files.exists(path)) {
                JsonObject json = JsonParser.parseString(Files.readString(path, StandardCharsets.UTF_8)).getAsJsonObject();
                config.mycosisEnabled = bool(json, "mycosis_enabled", config.mycosisEnabled);
                config.mycosisRising = bool(json, "mycosis_rising", config.mycosisRising);
                config.mycosisDamageInterval = Math.max(10, integer(json, "mycosis_damage_interval", config.mycosisDamageInterval));
                config.myceliarchHealth = Math.max(1.0, number(json, "myceliarch_health", config.myceliarchHealth));
                config.myceliarchDamageMultiplier = Math.max(0.0, number(json, "myceliarch_damage_multiplier", config.myceliarchDamageMultiplier));
                config.sporelingShedMin = Math.max(1, integer(json, "sporeling_shed_min", config.sporelingShedMin));
                config.sporelingShedMax = Math.max(config.sporelingShedMin, integer(json, "sporeling_shed_max", config.sporelingShedMax));
                config.trufflerDigChance = Math.max(0.0, Math.min(1.0, number(json, "truffler_dig_chance", config.trufflerDigChance)));
            }
            Files.createDirectories(path.getParent());
            Files.writeString(path, GSON.toJson(config.toJson()), StandardCharsets.UTF_8);
        } catch (IOException | RuntimeException e) {
            SporeAndStem.LOGGER.error("Could not read {}, using defaults", path, e);
        }
        instance = config;
    }

    private JsonObject toJson() {
        JsonObject json = new JsonObject();
        put(json, "mycosis_enabled", mycosisEnabled, "Mycosis infects (Shamblers, Deathcaps, spore clouds). false makes everyone shrug it off.");
        put(json, "mycosis_rising", mycosisRising, "Zombies, villagers, illagers, witches and players that die with Mycosis rise as Shamblers.");
        put(json, "mycosis_damage_interval", mycosisDamageInterval, "Ticks between Mycosis damage at level I (halved per level). Never below 10.");
        put(json, "myceliarch_health", myceliarchHealth, "The Myceliarch's maximum health.");
        put(json, "myceliarch_damage_multiplier", myceliarchDamageMultiplier, "Multiplies every attack of the Myceliarch.");
        put(json, "sporeling_shed_min", sporelingShedMin, "Minutes, at least, between the mushrooms a tamed Sporeling sheds.");
        put(json, "sporeling_shed_max", sporelingShedMax, "Minutes, at most, between the mushrooms a tamed Sporeling sheds.");
        put(json, "truffler_dig_chance", trufflerDigChance, "Chance (0-1) that a Truffler's sniff turns up a Truffle.");
        return json;
    }

    private static void put(JsonObject json, String key, Object value, String comment) {
        json.addProperty("_comment_" + key, comment);
        json.add(key, GSON.toJsonTree(value));
    }

    private static boolean bool(JsonObject json, String key, boolean fallback) {
        JsonElement e = json.get(key);
        return e != null && e.isJsonPrimitive() ? e.getAsBoolean() : fallback;
    }

    private static int integer(JsonObject json, String key, int fallback) {
        JsonElement e = json.get(key);
        return e != null && e.isJsonPrimitive() ? e.getAsInt() : fallback;
    }

    private static double number(JsonObject json, String key, double fallback) {
        JsonElement e = json.get(key);
        return e != null && e.isJsonPrimitive() ? e.getAsDouble() : fallback;
    }
}
