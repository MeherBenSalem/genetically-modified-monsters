package com.nightbeam.sporeandstem.worldgen;

import com.mojang.serialization.Codec;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;

import java.util.ArrayList;
import java.util.List;

/**
 * A fairy ring: one species of mushroom in a near-perfect circle on open, fairly level ground, with the odd gap.
 * Skips slopes (more than two blocks of height difference around the ring) so rings always read as circles.
 */
public class FairyRingFeature extends Feature<FairyRingConfiguration> {

    public FairyRingFeature(Codec<FairyRingConfiguration> codec) {
        super(codec);
    }

    @Override
    public boolean place(FeaturePlaceContext<FairyRingConfiguration> context) {
        WorldGenLevel level = context.level();
        RandomSource random = context.random();
        BlockPos origin = context.origin();
        FairyRingConfiguration config = context.config();
        int radius = config.radius().sample(random);
        BlockState fungus = config.fungus().getState(random, origin);
        List<BlockPos> ring = new ArrayList<>();
        int minY = Integer.MAX_VALUE;
        int maxY = Integer.MIN_VALUE;
        for (int dx = -radius - 1; dx <= radius + 1; dx++) {
            for (int dz = -radius - 1; dz <= radius + 1; dz++) {
                double distance = Math.sqrt(dx * dx + dz * dz);
                if (Math.abs(distance - radius) > 0.5) {
                    continue;
                }
                int x = origin.getX() + dx;
                int z = origin.getZ() + dz;
                int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
                minY = Math.min(minY, y);
                maxY = Math.max(maxY, y);
                ring.add(new BlockPos(x, y, z));
            }
        }
        if (ring.isEmpty() || maxY - minY > 2) {
            return false;
        }
        int placed = 0;
        for (BlockPos pos : ring) {
            if (random.nextFloat() < 0.12F) {
                continue;
            }
            BlockState here = level.getBlockState(pos);
            boolean free = here.isAir() || (here.is(BlockTags.REPLACEABLE_BY_TREES) && here.getFluidState().isEmpty()
                    && !here.is(BlockTags.LEAVES));
            if (free && fungus.canSurvive(level, pos)) {
                level.setBlock(pos, fungus, 2);
                placed++;
            }
        }
        if (placed > 0 && random.nextFloat() < config.centerChance()) {
            BlockPos center = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, origin);
            BlockState below = level.getBlockState(center.below());
            if (level.isEmptyBlock(center) && isDirt(below)) {
                level.setBlock(center, ModBlocks.GIANT_PUFFBALL.get().defaultBlockState(), 2);
            }
        }
        return placed > 0;
    }
}
