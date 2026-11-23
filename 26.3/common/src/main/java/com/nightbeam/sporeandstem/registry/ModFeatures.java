package com.nightbeam.sporeandstem.registry;

import com.mojang.serialization.MapCodec;
import com.nightbeam.sporeandstem.platform.Services;
import com.nightbeam.sporeandstem.worldgen.FairyRingFeature;
import com.nightbeam.sporeandstem.worldgen.HugeBouncecapFeature;
import com.nightbeam.sporeandstem.worldgen.HugeGlowcapFeature;
import com.nightbeam.sporeandstem.worldgen.HugeInkcapFeature;
import com.nightbeam.sporeandstem.worldgen.MycelialVeilFeature;
import com.nightbeam.sporeandstem.worldgen.ShelfFungusFeature;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;

/**
 * Custom worldgen feature types (huge fungi, shelf fungus, veils, fairy rings). Since 26.3 a feature type is the
 * codec of a feature record, registered in {@code Registries.FEATURE_TYPE}; the features themselves are data in the
 * generated resources (tools/assets/ss/worldgen.py).
 */
public final class ModFeatures {
    public static final RegistryEntry<MapCodec<? extends Feature>> HUGE_GLOWCAP = feature("huge_glowcap", HugeGlowcapFeature.CODEC);
    public static final RegistryEntry<MapCodec<? extends Feature>> HUGE_BOUNCECAP = feature("huge_bouncecap", HugeBouncecapFeature.CODEC);
    public static final RegistryEntry<MapCodec<? extends Feature>> HUGE_INKCAP = feature("huge_inkcap", HugeInkcapFeature.CODEC);
    public static final RegistryEntry<MapCodec<? extends Feature>> SHELF_FUNGUS = feature("shelf_fungus", ShelfFungusFeature.CODEC);
    public static final RegistryEntry<MapCodec<? extends Feature>> MYCELIAL_VEIL = feature("mycelial_veil", MycelialVeilFeature.CODEC);
    public static final RegistryEntry<MapCodec<? extends Feature>> FAIRY_RING = feature("fairy_ring", FairyRingFeature.CODEC);

    private ModFeatures() {
    }

    private static RegistryEntry<MapCodec<? extends Feature>> feature(String name, MapCodec<? extends Feature> codec) {
        return Services.REGISTRAR.register(Registries.FEATURE_TYPE, name, () -> codec);
    }

    public static void init() {
    }
}
