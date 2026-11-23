package com.nightbeam.sporeandstem.worldgen;

import com.mojang.serialization.Codec;
import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import org.jetbrains.annotations.Nullable;

/**
 * Base of the three huge fungi. Builds the whole shape into a {@link FungusPlan}, checks it has room, then places it.
 * Places nothing and returns false when it does not fit (bone meal relies on this to keep the small mushroom).
 */
public abstract class HugeFungusFeature extends Feature<HugeFungusConfiguration> {

    protected HugeFungusFeature(Codec<HugeFungusConfiguration> codec) {
        super(codec);
    }

    /** Fills the plan. {@code height} is the stem height and {@code radius} the cap radius from the configuration. */
    protected abstract void shape(FungusPlan plan, RandomSource random, int height, int radius);

    protected abstract BlockState stem();

    protected abstract BlockState cap();

    @Nullable
    protected BlockState hanger() {
        return null;
    }

    @Nullable
    protected BooleanProperty hangerTip() {
        return null;
    }

    @Override
    public boolean place(FeaturePlaceContext<HugeFungusConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        HugeFungusConfiguration config = context.config();
        if (!FungusPlan.isFree(level, origin) || !isGround(level, origin.below(), config.anyGround())) {
            return false;
        }
        FungusPlan plan = new FungusPlan(origin);
        shape(plan, random, config.height().sample(random), config.radius().sample(random));
        if (!plan.fits(level)) {
            return false;
        }
        plan.place(level, stem(), cap(), hanger(), hangerTip());
        return true;
    }

    static boolean isGround(WorldGenLevel level, BlockPos pos, boolean anyGround) {
        BlockState state = level.getBlockState(pos);
        if (isDirt(state) || state.is(BlockTags.MUSHROOM_GROW_BLOCK) || state.is(ModTags.Blocks.FUNGUS_SOIL)) {
            return true;
        }
        return anyGround && state.getFluidState().isEmpty() && state.isFaceSturdy(level, pos, Direction.UP);
    }

    /** A round disc of the given radius, a little fuller than a circle so edges don't look jagged. */
    static boolean inDisc(int dx, int dz, double radius, double fullness) {
        return dx * dx + dz * dz <= radius * radius + radius * fullness;
    }
}
