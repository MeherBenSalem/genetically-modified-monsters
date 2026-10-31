package com.nightbeam.sporeandstem.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.util.valueproviders.IntProvider;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;

/**
 * Size of a huge fungus. {@code height} is the stem height, {@code radius} the cap radius. {@code any_ground} lets it
 * stand on any solid block (cave floors); otherwise it needs dirt-like ground, mycelium, moss or Mycelial Soil.
 */
public record HugeFungusConfiguration(IntProvider height, IntProvider radius, boolean anyGround) implements FeatureConfiguration {
    public static final Codec<HugeFungusConfiguration> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            IntProvider.codec(1, 32).fieldOf("height").forGetter(HugeFungusConfiguration::height),
            IntProvider.codec(1, 6).fieldOf("radius").forGetter(HugeFungusConfiguration::radius),
            Codec.BOOL.optionalFieldOf("any_ground", false).forGetter(HugeFungusConfiguration::anyGround)
    ).apply(instance, HugeFungusConfiguration::new));
}
