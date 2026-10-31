package com.nightbeam.sporeandstem.block;

import com.mojang.serialization.MapCodec;
import com.nightbeam.sporeandstem.content.CultivationFungus;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraft.core.Direction.Axis;

/**
 * A felled log lying on its side, ready to grow mushrooms. Use a fungus on a fresh log to inoculate it; it fruits
 * through four stages on random ticks (faster on Mycelial Soil, slower under the open sky in daylight). Use a ripe
 * log to harvest it; it falls back to its first flush and fruits again.
 */
public class CultivationLogBlock extends Block {
    public static final MapCodec<CultivationLogBlock> CODEC = simpleCodec(CultivationLogBlock::new);
    public static final EnumProperty<Axis> AXIS = BlockStateProperties.HORIZONTAL_AXIS;
    public static final EnumProperty<CultivationFungus> FUNGUS = EnumProperty.create("fungus", CultivationFungus.class);
    public static final IntegerProperty STAGE = IntegerProperty.create("stage", 0, 3);
    private static final VoxelShape SHAPE_X = Block.box(0.0, 0.0, 2.0, 16.0, 12.0, 14.0);
    private static final VoxelShape SHAPE_Z = Block.box(2.0, 0.0, 0.0, 14.0, 12.0, 16.0);

    public CultivationLogBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(AXIS, Axis.X)
                .setValue(FUNGUS, CultivationFungus.NONE).setValue(STAGE, 0));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(AXIS, FUNGUS, STAGE);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return this.defaultBlockState().setValue(AXIS, context.getHorizontalDirection().getAxis());
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(AXIS) == Axis.X ? SHAPE_X : SHAPE_Z;
    }

    @Override
    protected BlockState rotate(BlockState state, Rotation rotation) {
        if (rotation == Rotation.CLOCKWISE_90 || rotation == Rotation.COUNTERCLOCKWISE_90) {
            return state.setValue(AXIS, state.getValue(AXIS) == Axis.X ? Axis.Z : Axis.X);
        }
        return state;
    }

    @Override
    protected BlockState mirror(BlockState state, Mirror mirror) {
        return state;
    }

    public static boolean isRipe(BlockState state) {
        return state.getValue(FUNGUS) != CultivationFungus.NONE && state.getValue(STAGE) == 3;
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        if (state.getValue(FUNGUS) != CultivationFungus.NONE) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        CultivationFungus fungus = CultivationFungus.of(stack);
        if (fungus == CultivationFungus.NONE) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        if (!level.isClientSide) {
            level.setBlock(pos, state.setValue(FUNGUS, fungus).setValue(STAGE, 0), 3);
            level.playSound(null, pos, ModSounds.CULTIVATION_LOG_INOCULATE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
            ((ServerLevel) level).sendParticles(ModParticles.SPORE.get(), pos.getX() + 0.5, pos.getY() + 0.8,
                    pos.getZ() + 0.5, 14, 0.35, 0.15, 0.35, 0.01);
            level.gameEvent(GameEvent.BLOCK_CHANGE, pos, GameEvent.Context.of(player, state));
            stack.consume(1, player);
        }
        return ItemInteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!isRipe(state)) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide) {
            int count = 2 + level.random.nextInt(2);
            popResourceFromFace(level, pos, Direction.UP, new ItemStack(state.getValue(FUNGUS).item(), count));
            level.setBlock(pos, state.setValue(STAGE, 1), 3);
            level.playSound(null, pos, ModSounds.CULTIVATION_LOG_HARVEST.get(), SoundSource.BLOCKS, 1.0F,
                    0.9F + level.random.nextFloat() * 0.2F);
            level.gameEvent(GameEvent.BLOCK_CHANGE, pos, GameEvent.Context.of(player, state));
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected boolean isRandomlyTicking(BlockState state) {
        return state.getValue(FUNGUS) != CultivationFungus.NONE && state.getValue(STAGE) < 3;
    }

    @Override
    protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        int odds = 4;
        if (level.getBlockState(pos.below()).is(ModBlocks.MYCELIAL_SOIL.get())) {
            odds = 2;
        } else if (level.canSeeSky(pos.above()) && level.isDay()) {
            odds = 8;
        }
        if (random.nextInt(odds) == 0) {
            level.setBlock(pos, state.setValue(STAGE, state.getValue(STAGE) + 1), 2);
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (isRipe(state) && random.nextInt(5) == 0) {
            level.addParticle(state.getValue(FUNGUS) == CultivationFungus.GLOWCAP ? ModParticles.GLOW_SPORE.get()
                            : ModParticles.SPORE.get(), pos.getX() + 0.2 + random.nextDouble() * 0.6, pos.getY() + 0.9,
                    pos.getZ() + 0.2 + random.nextDouble() * 0.6, 0.0, 0.01, 0.0);
        } else if (state.getValue(FUNGUS) == CultivationFungus.EMBERSTOOL && state.getValue(STAGE) > 1 && random.nextInt(10) == 0) {
            level.addParticle(ParticleTypes.SMALL_FLAME, pos.getX() + 0.3 + random.nextDouble() * 0.4, pos.getY() + 0.95,
                    pos.getZ() + 0.3 + random.nextDouble() * 0.4, 0.0, 0.005, 0.0);
        }
    }
}
