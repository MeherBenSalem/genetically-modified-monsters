package com.nightbeam.sporeandstem.worldgen;

import com.nightbeam.sporeandstem.SporeAndStem;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.levelgen.feature.Feature;

/** Keys of features referenced from code (26.3 folds configured features into Registries.FEATURE). The JSON lives in the generated data. */
public final class ModConfiguredFeatures {
    public static final ResourceKey<Feature> HUGE_GLOWCAP = key("huge_glowcap");
    public static final ResourceKey<Feature> HUGE_BOUNCECAP = key("huge_bouncecap");
    public static final ResourceKey<Feature> HUGE_INKCAP = key("huge_inkcap");

    private ModConfiguredFeatures() {
    }

    private static ResourceKey<Feature> key(String name) {
        return ResourceKey.create(Registries.FEATURE, SporeAndStem.id(name));
    }
}
