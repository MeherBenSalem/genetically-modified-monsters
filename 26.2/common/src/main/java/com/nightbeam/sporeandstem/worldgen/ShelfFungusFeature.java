package com.nightbeam.sporeandstem.worldgen;

import com.mojang.serialization.Codec;
import com.nightbeam.sporeandstem.block.ShelfFungusBlock;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.CountConfiguration;

/**
 * Turkey-tail brackets on tree trunks around the origin. Each try looks for a free spot beside a log or stem; a hit
 * often gets a second bracket stacked a block or two above or below on the same side, the way they grow.
 */
public class ShelfFungusFeature extends Feature<CountConfiguration> {

    public ShelfFungusFeature(Codec<CountConfiguration> codec) {
        super(codec);
    }

    @Override
    public boolean place(FeaturePlaceContext<CountConfiguration> context) {
        WorldGenLevel level = context.level();
        RandomSource random = context.random();
        BlockPos origin = context.origin();
        int tries = context.config().count().sample(random);
        int placed = 0;
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        for (int i = 0; i < tries; i++) {
            pos.setWithOffset(origin, random.nextInt(13) - 6, random.nextInt(11) - 1, random.nextInt(13) - 6);
            Direction facing = attach(level, pos, random);
            if (facing == null) {
                continue;
            }
            if (setShelf(level, pos.immutable(), facing, random)) {
                placed++;
                int stack = random.nextInt(3);
                for (int s = 0; s < stack; s++) {
                    BlockPos other = pos.above(random.nextBoolean() ? 1 + s : -1 - s);
                    if (level.isEmptyBlock(other) && setShelf(level, other, facing, random)) {
                        placed++;
                    }
                }
            }
        }
        return placed > 0;
    }

    /** The side facing away from an adjacent trunk, or null when the spot isn't free next to one. */
    private static Direction attach(WorldGenLevel level, BlockPos pos, RandomSource random) {
        if (!level.isEmptyBlock(pos)) {
            return null;
        }
        Direction start = Direction.Plane.HORIZONTAL.getRandomDirection(random);
        for (int i = 0; i < 4; i++) {
            Direction toTrunk = Direction.from2DDataValue((start.get2DDataValue() + i) % 4);
            if (level.getBlockState(pos.relative(toTrunk)).is(ModTags.Blocks.SHELF_FUNGUS_HOSTS)) {
                return toTrunk.getOpposite();
            }
        }
        return null;
    }

    private static boolean setShelf(WorldGenLevel level, BlockPos pos, Direction facing, RandomSource random) {
        float roll = random.nextFloat();
        int shelves = roll < 0.45F ? 1 : roll < 0.8F ? 2 : 3;
        BlockState state = ModBlocks.SHELF_FUNGUS.get().defaultBlockState()
                .setValue(ShelfFungusBlock.FACING, facing).setValue(ShelfFungusBlock.SHELVES, shelves);
        if (!state.canSurvive(level, pos)) {
            return false;
        }
        level.setBlock(pos, state, 2);
        return true;
    }
}
