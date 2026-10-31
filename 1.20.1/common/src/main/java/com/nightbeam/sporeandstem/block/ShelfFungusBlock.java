package com.nightbeam.sporeandstem.block;

import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.EnumMap;
import java.util.Map;

/**
 * Turkey-tail brackets on the side of a log or stem. FACING points away from the host trunk. One to three shelves:
 * it grows on random ticks, and placing another on it adds a shelf. The shelves are solid: you can climb them.
 */
public class ShelfFungusBlock extends HorizontalDirectionalBlock {
    public static final IntegerProperty SHELVES = IntegerProperty.create("shelves", 1, 3);
    /** Shelf heights and reach (pixels out from the trunk), bottom to top. Matches the block models. */
    private static final int[][] SHELF = {{3, 5, 7}, {8, 10, 6}, {12, 14, 5}};
    private static final Map<Direction, VoxelShape[]> SHAPES = new EnumMap<>(Direction.class);

    static {
        for (Direction facing : Direction.Plane.HORIZONTAL) {
            VoxelShape[] byCount = new VoxelShape[3];
            VoxelShape acc = Shapes.empty();
            for (int i = 0; i < 3; i++) {
                acc = Shapes.or(acc, plate(facing, SHELF[i][0], SHELF[i][1], SHELF[i][2], i));
                byCount[i] = acc;
            }
            SHAPES.put(facing, byCount);
        }
    }

    private static VoxelShape plate(Direction facing, int y0, int y1, int reach, int index) {
        // Each shelf is offset sideways a little so the brackets stagger like real ones.
        int side = index == 1 ? 1 : (index == 2 ? 5 : 3);
        int width = index == 1 ? 9 : (index == 2 ? 8 : 11);
        double a = side;
        double b = side + width;
        return switch (facing) {
            case SOUTH -> Block.box(a, y0, 0.0, b, y1, reach);
            case NORTH -> Block.box(16.0 - b, y0, 16.0 - reach, 16.0 - a, y1, 16.0);
            case EAST -> Block.box(0.0, y0, 16.0 - b, reach, y1, 16.0 - a);
            default -> Block.box(16.0 - reach, y0, a, 16.0, y1, b);
        };
    }

    public ShelfFungusBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(SHELVES, 1));
    }


    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, SHELVES);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPES.get(state.getValue(FACING))[state.getValue(SHELVES) - 1];
    }

    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        return level.getBlockState(pos.relative(state.getValue(FACING).getOpposite())).is(ModTags.Blocks.SHELF_FUNGUS_HOSTS);
    }

    @Override
    public boolean canBeReplaced(BlockState state, BlockPlaceContext context) {
        return !context.isSecondaryUseActive() && context.getItemInHand().is(this.asItem()) && state.getValue(SHELVES) < 3
                || super.canBeReplaced(state, context);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState existing = context.getLevel().getBlockState(context.getClickedPos());
        if (existing.is(this)) {
            return existing.setValue(SHELVES, Math.min(3, existing.getValue(SHELVES) + 1));
        }
        Direction clicked = context.getClickedFace();
        if (clicked.getAxis().isHorizontal()) {
            BlockState state = this.defaultBlockState().setValue(FACING, clicked);
            if (state.canSurvive(context.getLevel(), context.getClickedPos())) {
                return state;
            }
        }
        for (Direction direction : context.getNearestLookingDirections()) {
            if (direction.getAxis().isHorizontal()) {
                BlockState state = this.defaultBlockState().setValue(FACING, direction.getOpposite());
                if (state.canSurvive(context.getLevel(), context.getClickedPos())) {
                    return state;
                }
            }
        }
        return null;
    }

    @Override
    public BlockState updateShape(BlockState state, Direction direction, BlockState neighbor, LevelAccessor level,
                                     BlockPos pos, BlockPos neighborPos) {
        if (direction == state.getValue(FACING).getOpposite() && !state.canSurvive(level, pos)) {
            return Blocks.AIR.defaultBlockState();
        }
        return state;
    }

    @Override
    public boolean isRandomlyTicking(BlockState state) {
        return state.getValue(SHELVES) < 3;
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (random.nextInt(12) == 0) {
            level.setBlock(pos, state.setValue(SHELVES, state.getValue(SHELVES) + 1), 2);
        }
    }
}
