package com.nightbeam.sporeandstem.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.util.valueproviders.IntProvider;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;
import net.minecraft.world.level.levelgen.feature.stateproviders.BlockStateProvider;

/**
 * A fairy ring: {@code fungus} picks the one species of the whole ring, {@code radius} its size, and
 * {@code center_chance} the chance of a Giant Puffball sitting in the middle.
 */
public record FairyRingConfiguration(BlockStateProvider fungus, IntProvider radius, float centerChance) implements FeatureConfiguration {
    public static final Codec<FairyRingConfiguration> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            BlockStateProvider.CODEC.fieldOf("fungus").forGetter(FairyRingConfiguration::fungus),
            IntProvider.codec(2, 7).fieldOf("radius").forGetter(FairyRingConfiguration::radius),
            Codec.floatRange(0.0F, 1.0F).optionalFieldOf("center_chance", 0.0F).forGetter(FairyRingConfiguration::centerChance)
    ).apply(instance, FairyRingConfiguration::new));
}
