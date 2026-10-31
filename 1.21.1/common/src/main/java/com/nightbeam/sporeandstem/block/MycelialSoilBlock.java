package com.nightbeam.sporeandstem.block;

import com.mojang.serialization.MapCodec;
import com.nightbeam.sporeandstem.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.MushroomBlock;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Dark loam threaded with mycelium. Mushrooms (vanilla too) survive on it in any light, and it feeds the mushroom
 * above it on random ticks: small fungi spread, and huge-growing ones may grow huge.
 */
public class MycelialSoilBlock extends Block {
    public static final MapCodec<MycelialSoilBlock> CODEC = simpleCodec(MycelialSoilBlock::new);

    public MycelialSoilBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected boolean isRandomlyTicking(BlockState state) {
        return true;
    }

    @Override
    protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        BlockPos abovePos = pos.above();
        BlockState above = level.getBlockState(abovePos);
        if (above.getBlock() instanceof FungusBlock fungus) {
            if (fungus.growsHuge()) {
                if (random.nextInt(40) == 0) {
                    fungus.growMushroom(level, abovePos, above, random);
                } else if (random.nextInt(10) == 0) {
                    FungusBlock.spread(level, abovePos, above, random);
                }
            } else if (random.nextInt(8) == 0) {
                FungusBlock.spread(level, abovePos, above, random);
            }
        } else if (above.getBlock() instanceof MushroomBlock && random.nextInt(8) == 0) {
            FungusBlock.spread(level, abovePos, above, random);
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(14) == 0 && level.getBlockState(pos.above()).isAir()) {
            level.addParticle(ModParticles.SPORE.get(), pos.getX() + random.nextDouble(), pos.getY() + 1.05,
                    pos.getZ() + random.nextDouble(), 0.0, 0.01, 0.0);
        }
    }
}
