package com.nightbeam.sporeandstem.block;

import com.nightbeam.sporeandstem.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.HugeMushroomBlock;
import net.minecraft.world.level.block.state.BlockState;

/** An Inkcap's cap: wherever its underside is open to the air, it drips ink. */
public class InkcapCapBlock extends HugeMushroomBlock {

    public InkcapCapBlock(Properties properties) {
        super(properties);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(6) == 0 && level.isEmptyBlock(pos.below())) {
            double x = pos.getX() + 0.15 + random.nextDouble() * 0.7;
            double z = pos.getZ() + 0.15 + random.nextDouble() * 0.7;
            level.addParticle(ModParticles.INK_DRIP.get(), x, pos.getY() - 0.05, z, 0.0, 0.0, 0.0);
        }
    }
}
