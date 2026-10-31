package com.nightbeam.sporeandstem.platform.services;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;

import java.nio.file.Path;
import java.util.function.Supplier;

/** Loader-specific facts and builders the common code needs. */
public interface IPlatformHelper {

    /** "Fabric" or "Forge". */
    String getPlatformName();

    boolean isDevelopmentEnvironment();

    Path getConfigDirectory();

    /** A creative tab builder positioned the way the loader expects. */
    CreativeModeTab.Builder creativeTabBuilder();

    /**
     * A spawn egg. Forge 1.20.1 registers items before entity types, so the egg must resolve its type lazily there.
     */
    Item spawnEgg(Supplier<? extends EntityType<? extends Mob>> type, int base, int spots, Item.Properties properties);

    /**
     * Adds an effect of this mod to a food. Forge 1.20.1 registers items before mob effects, so the effect is
     * resolved lazily there.
     */
    FoodProperties.Builder modEffect(FoodProperties.Builder builder, Supplier<MobEffectInstance> effect, float chance);
}
