package com.nightbeam.sporeandstem.worldgen;

import com.mojang.serialization.Codec;
import com.nightbeam.sporeandstem.block.VeilBulbs;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.GrowingPlantHeadBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.CountConfiguration;

/**
 * A cluster of Mycelial Veil strands hanging from a ceiling near the origin (placed just under a sturdy ceiling).
 * Strands are 2-8 blocks long; some segments carry glowing bulbs.
 */
public class MycelialVeilFeature extends Feature<CountConfiguration> {

    public MycelialVeilFeature(Codec<CountConfiguration> codec) {
        super(codec);
    }

    @Override
    public boolean place(FeaturePlaceContext<CountConfiguration> context) {
        WorldGenLevel level = context.level();
        RandomSource random = context.random();
        BlockPos origin = context.origin();
        int strands = context.config().count().sample(random);
        int placed = 0;
        for (int i = 0; i < strands; i++) {
            BlockPos start = findUnderCeiling(level, origin.offset(random.nextInt(7) - 3, 0, random.nextInt(7) - 3));
            if (start != null && strand(level, start, 2 + random.nextInt(7), random)) {
                placed++;
            }
        }
        return placed > 0;
    }

    /** The air block right under a sturdy ceiling, searching a few blocks up and down from {@code pos}. */
    private static BlockPos findUnderCeiling(WorldGenLevel level, BlockPos pos) {
        BlockPos.MutableBlockPos cursor = pos.mutable();
        for (int dy = -2; dy <= 4; dy++) {
            cursor.setWithOffset(pos, 0, dy, 0);
            if (level.isEmptyBlock(cursor)) {
                BlockPos above = cursor.above();
                if (level.getBlockState(above).isFaceSturdy(level, above, Direction.DOWN)) {
                    return cursor.immutable();
                }
            }
        }
        return null;
    }

    private static boolean strand(WorldGenLevel level, BlockPos top, int wanted, RandomSource random) {
        int length = 0;
        while (length < wanted && level.isEmptyBlock(top.below(length)) && !level.isOutsideBuildHeight(top.below(length))) {
            length++;
        }
        if (length == 0) {
            return false;
        }
        BlockState body = ModBlocks.MYCELIAL_VEIL_PLANT.get().defaultBlockState();
        BlockState head = ModBlocks.MYCELIAL_VEIL.get().defaultBlockState()
                .setValue(GrowingPlantHeadBlock.AGE, 18 + random.nextInt(8));
        for (int i = 0; i < length; i++) {
            boolean last = i == length - 1;
            BlockState state = (last ? head : body).setValue(VeilBulbs.BULB, random.nextFloat() < (last ? 0.3F : 0.15F));
            level.setBlock(top.below(i), state, 2);
        }
        return true;
    }
}
