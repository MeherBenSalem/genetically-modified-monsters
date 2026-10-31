package com.nightbeam.sporeandstem.worldgen;

import com.nightbeam.sporeandstem.SporeAndStem;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;

/** Keys of configured features referenced from code. The JSON lives in the generated data. */
public final class ModConfiguredFeatures {
    public static final ResourceKey<ConfiguredFeature<?, ?>> HUGE_GLOWCAP = key("huge_glowcap");
    public static final ResourceKey<ConfiguredFeature<?, ?>> HUGE_BOUNCECAP = key("huge_bouncecap");
    public static final ResourceKey<ConfiguredFeature<?, ?>> HUGE_INKCAP = key("huge_inkcap");

    private ModConfiguredFeatures() {
    }

    private static ResourceKey<ConfiguredFeature<?, ?>> key(String name) {
        return ResourceKey.create(Registries.CONFIGURED_FEATURE, SporeAndStem.id(name));
    }
}
