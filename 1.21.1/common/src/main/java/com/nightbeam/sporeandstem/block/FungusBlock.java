package com.nightbeam.sporeandstem.block;

import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.data.worldgen.features.TreeFeatures;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.MushroomBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * A small placeable mushroom with a real 3D model. Survives in any light on fungus soil (dirt-like blocks, moss,
 * mycelium, Mycelial Soil) and on any solid block in the dark. Bone meal grows it into its huge fungus when it has
 * one, otherwise spreads a copy nearby. It only spreads by itself in the dark or on mycelium.
 */
public class FungusBlock extends MushroomBlock {
    @Nullable
    private final ResourceKey<ConfiguredFeature<?, ?>> hugeFeature;
    private final VoxelShape shape;

    public FungusBlock(@Nullable ResourceKey<ConfiguredFeature<?, ?>> hugeFeature, VoxelShape shape, Properties properties) {
        // MushroomBlock needs a feature key; spreading fungi never use it (growMushroom is overridden).
        super(hugeFeature != null ? hugeFeature : TreeFeatures.HUGE_BROWN_MUSHROOM, properties);
        this.hugeFeature = hugeFeature;
        this.shape = shape;
    }

    public boolean growsHuge() {
        return hugeFeature != null;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        Vec3 offset = state.getOffset(level, pos);
        return shape.move(offset.x, offset.y, offset.z);
    }

    public static boolean isFungusSoil(BlockState below) {
        return below.is(BlockTags.MUSHROOM_GROW_BLOCK) || below.is(ModTags.Blocks.FUNGUS_SOIL);
    }

    @Override
    protected boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockPos belowPos = pos.below();
        BlockState below = level.getBlockState(belowPos);
        if (isFungusSoil(below)) {
            return true;
        }
        return level.getRawBrightness(pos, 0) < 13 && this.mayPlaceOn(below, level, belowPos);
    }

    @Override
    protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        BlockState below = level.getBlockState(pos.below());
        boolean fertile = below.is(BlockTags.MUSHROOM_GROW_BLOCK) || level.getRawBrightness(pos, 0) < 13;
        if (fertile) {
            super.randomTick(state, level, pos, random);
        }
    }

    @Override
    public boolean isBonemealSuccess(Level level, RandomSource random, BlockPos pos, BlockState state) {
        return growsHuge() ? random.nextFloat() < 0.4F : random.nextFloat() < 0.6F;
    }

    @Override
    public void performBonemeal(ServerLevel level, RandomSource random, BlockPos pos, BlockState state) {
        if (growsHuge()) {
            this.growMushroom(level, pos, state, random);
        } else {
            spread(level, pos, state, random);
        }
    }

    @Override
    public boolean growMushroom(ServerLevel level, BlockPos pos, BlockState state, RandomSource random) {
        return growsHuge() && super.growMushroom(level, pos, state, random);
    }

    /** Places a copy on a free, survivable spot within three blocks. */
    public static boolean spread(ServerLevel level, BlockPos pos, BlockState state, RandomSource random) {
        for (int i = 0; i < 12; i++) {
            BlockPos target = pos.offset(random.nextInt(7) - 3, random.nextInt(3) - 1, random.nextInt(7) - 3);
            if (level.isEmptyBlock(target) && state.canSurvive(level, target)) {
                level.setBlock(target, state, 3);
                return true;
            }
        }
        return false;
    }
}
