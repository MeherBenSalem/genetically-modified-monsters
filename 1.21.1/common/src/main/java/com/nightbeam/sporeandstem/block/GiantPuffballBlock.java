package com.nightbeam.sporeandstem.block;

import com.mojang.serialization.MapCodec;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/** A soft giant puffball: landing on it (or breaking it) puffs a cloud of spores, and it halves fall damage. */
public class GiantPuffballBlock extends Block {
    public static final MapCodec<GiantPuffballBlock> CODEC = simpleCodec(GiantPuffballBlock::new);

    public GiantPuffballBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    public void fallOn(Level level, BlockState state, BlockPos pos, Entity entity, float fallDistance) {
        if (fallDistance > 1.0F) {
            puff(level, pos, Math.min(40, 8 + (int) (fallDistance * 4)));
        }
        entity.causeFallDamage(fallDistance, 0.5F, level.damageSources().fall());
    }

    @Override
    public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
        puff(level, pos, 24);
        return super.playerWillDestroy(level, pos, state, player);
    }

    public static void puff(Level level, BlockPos pos, int count) {
        if (level instanceof ServerLevel server) {
            server.sendParticles(ModParticles.SPORE.get(), pos.getX() + 0.5, pos.getY() + 1.05, pos.getZ() + 0.5, count,
                    0.45, 0.2, 0.45, 0.02);
            float pitch = 0.85F + level.random.nextFloat() * 0.3F;
            level.playSound(null, pos, ModSounds.GIANT_PUFFBALL_PUFF.get(), SoundSource.BLOCKS, 0.9F, pitch);
        }
    }
}
