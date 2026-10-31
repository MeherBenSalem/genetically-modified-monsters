package com.nightbeam.sporeandstem.block;

import com.mojang.serialization.MapCodec;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Luminous gill curtains that hang under a Glowcap's cap (or any ceiling), one or two blocks long. TIP marks the
 * lowest block, which tapers off.
 */
public class GlowcapGillsBlock extends Block {
    public static final MapCodec<GlowcapGillsBlock> CODEC = simpleCodec(GlowcapGillsBlock::new);
    public static final BooleanProperty TIP = BlockStateProperties.BOTTOM;
    private static final VoxelShape SHAPE = Block.box(1.0, 0.0, 1.0, 15.0, 16.0, 15.0);
    private static final VoxelShape TIP_SHAPE = Block.box(2.0, 6.0, 2.0, 14.0, 16.0, 14.0);

    public GlowcapGillsBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(TIP, true));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(TIP);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(TIP) ? TIP_SHAPE : SHAPE;
    }

    @Override
    protected boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        BlockPos abovePos = pos.above();
        BlockState above = level.getBlockState(abovePos);
        return above.is(this) || above.is(ModBlocks.GLOWCAP_CAP.get()) || above.isFaceSturdy(level, abovePos, Direction.DOWN);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = this.defaultBlockState();
        if (!state.canSurvive(context.getLevel(), context.getClickedPos())) {
            return null;
        }
        return state.setValue(TIP, !context.getLevel().getBlockState(context.getClickedPos().below()).is(this));
    }

    @Override
    protected BlockState updateShape(BlockState state, Direction direction, BlockState neighbor, LevelAccessor level,
                                     BlockPos pos, BlockPos neighborPos) {
        if (direction == Direction.UP && !state.canSurvive(level, pos)) {
            return Blocks.AIR.defaultBlockState();
        }
        if (direction == Direction.DOWN) {
            return state.setValue(TIP, !neighbor.is(this));
        }
        return state;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (state.getValue(TIP) && random.nextInt(8) == 0) {
            double x = pos.getX() + 0.2 + random.nextDouble() * 0.6;
            double z = pos.getZ() + 0.2 + random.nextDouble() * 0.6;
            level.addParticle(ModParticles.GLOW_SPORE.get(), x, pos.getY() + 0.35, z, 0.0, -0.01, 0.0);
        }
    }
}
