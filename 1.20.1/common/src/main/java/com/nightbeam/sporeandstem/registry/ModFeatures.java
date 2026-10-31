package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.platform.Services;
import com.nightbeam.sporeandstem.worldgen.FairyRingConfiguration;
import com.nightbeam.sporeandstem.worldgen.FairyRingFeature;
import com.nightbeam.sporeandstem.worldgen.HugeBouncecapFeature;
import com.nightbeam.sporeandstem.worldgen.HugeFungusConfiguration;
import com.nightbeam.sporeandstem.worldgen.HugeGlowcapFeature;
import com.nightbeam.sporeandstem.worldgen.HugeInkcapFeature;
import com.nightbeam.sporeandstem.worldgen.MycelialVeilFeature;
import com.nightbeam.sporeandstem.worldgen.ShelfFungusFeature;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.CountConfiguration;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;

import java.util.function.Supplier;

/**
 * Custom worldgen feature types (huge fungi, shelf fungus, veils, fairy rings). Configured and placed features are
 * data in the generated resources (tools/assets/ss/worldgen.py).
 */
public final class ModFeatures {
    public static final RegistryEntry<Feature<HugeFungusConfiguration>> HUGE_GLOWCAP = feature("huge_glowcap",
            () -> new HugeGlowcapFeature(HugeFungusConfiguration.CODEC));
    public static final RegistryEntry<Feature<HugeFungusConfiguration>> HUGE_BOUNCECAP = feature("huge_bouncecap",
            () -> new HugeBouncecapFeature(HugeFungusConfiguration.CODEC));
    public static final RegistryEntry<Feature<HugeFungusConfiguration>> HUGE_INKCAP = feature("huge_inkcap",
            () -> new HugeInkcapFeature(HugeFungusConfiguration.CODEC));
    public static final RegistryEntry<Feature<CountConfiguration>> SHELF_FUNGUS = feature("shelf_fungus",
            () -> new ShelfFungusFeature(CountConfiguration.CODEC));
    public static final RegistryEntry<Feature<CountConfiguration>> MYCELIAL_VEIL = feature("mycelial_veil",
            () -> new MycelialVeilFeature(CountConfiguration.CODEC));
    public static final RegistryEntry<Feature<FairyRingConfiguration>> FAIRY_RING = feature("fairy_ring",
            () -> new FairyRingFeature(FairyRingConfiguration.CODEC));

    private ModFeatures() {
    }

    private static <C extends FeatureConfiguration> RegistryEntry<Feature<C>> feature(String name, Supplier<Feature<C>> factory) {
        return Services.REGISTRAR.register(Registries.FEATURE, name, factory);
    }

    public static void init() {
    }
}
