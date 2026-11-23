package com.nightbeam.sporeandstem.block;

import com.mojang.serialization.MapCodec;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.GrowingPlantHeadBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockBehaviour;

/** The growing tip of a Mycelial Veil: white threads hanging from a ceiling, sometimes carrying a glowing bulb. */
public class MycelialVeilBlock extends GrowingPlantHeadBlock {
    public static final MapCodec<MycelialVeilBlock> CODEC = simpleCodec(MycelialVeilBlock::new);
    private static final VoxelShape SHAPE = Block.box(3.0, 2.0, 3.0, 13.0, 16.0, 13.0);

    public MycelialVeilBlock(BlockBehaviour.Properties properties) {
        super(properties, Direction.DOWN, SHAPE, false, 0.08);
        this.registerDefaultState(this.stateDefinition.any().setValue(AGE, 0).setValue(VeilBulbs.BULB, false));
    }

    @Override
    protected MapCodec<? extends GrowingPlantHeadBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        super.createBlockStateDefinition(builder);
        builder.add(VeilBulbs.BULB);
    }

    @Override
    protected int getBlocksToGrowWhenBonemealed(RandomSource random) {
        return 1 + random.nextInt(2);
    }

    @Override
    protected boolean canGrowInto(BlockState state) {
        return state.isAir();
    }

    @Override
    protected Block getBodyBlock() {
        return ModBlocks.MYCELIAL_VEIL_PLANT.get();
    }

    @Override
    protected BlockState getGrowIntoState(BlockState state, RandomSource random) {
        return super.getGrowIntoState(state, random).setValue(VeilBulbs.BULB, random.nextFloat() < 0.18F);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = super.getStateForPlacement(context);
        return state == null ? null : state.setValue(VeilBulbs.BULB, false);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        return VeilBulbs.pick(player, state, level, pos);
    }

    @Override
    public boolean isValidBonemealTarget(LevelReader level, BlockPos pos, BlockState state) {
        return super.isValidBonemealTarget(level, pos, state) || !state.getValue(VeilBulbs.BULB);
    }
}
