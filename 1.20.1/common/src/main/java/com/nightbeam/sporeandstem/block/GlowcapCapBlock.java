package com.nightbeam.sporeandstem.block;

import com.nightbeam.sporeandstem.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.HugeMushroomBlock;
import net.minecraft.world.level.block.state.BlockState;

/** A Glowcap's cap: it glows, and now and then lets a luminous spore drift down from its open underside. */
public class GlowcapCapBlock extends HugeMushroomBlock {

    public GlowcapCapBlock(Properties properties) {
        super(properties);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(14) == 0 && level.isEmptyBlock(pos.below())) {
            double x = pos.getX() + random.nextDouble();
            double z = pos.getZ() + random.nextDouble();
            level.addParticle(ModParticles.GLOW_SPORE.get(), x, pos.getY() - 0.1, z, 0.0, -0.01, 0.0);
        }
    }
}
