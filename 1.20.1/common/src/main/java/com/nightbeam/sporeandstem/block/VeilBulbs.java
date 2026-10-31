package com.nightbeam.sporeandstem.block;

import com.nightbeam.sporeandstem.registry.ModItems;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.gameevent.GameEvent;

import java.util.function.ToIntFunction;

/** The glowing bulbs on Mycelial Veils, shared by head and body (like glow berries on cave vines). */
public final class VeilBulbs {
    public static final BooleanProperty BULB = BooleanProperty.create("bulb");

    private VeilBulbs() {
    }

    public static ToIntFunction<BlockState> light(int level) {
        return state -> state.getValue(BULB) ? level : 0;
    }

    static InteractionResult pick(Player player, BlockState state, Level level, BlockPos pos) {
        if (!state.getValue(BULB)) {
            return InteractionResult.PASS;
        }
        if (!level.isClientSide) {
            Block.popResource(level, pos, new ItemStack(ModItems.LUMEN_SPORES.get()));
            float pitch = 0.8F + level.random.nextFloat() * 0.4F;
            level.playSound(null, pos, ModSounds.MYCELIAL_VEIL_PICK.get(), SoundSource.BLOCKS, 1.0F, pitch);
            BlockState picked = state.setValue(BULB, false);
            level.setBlock(pos, picked, 2);
            level.gameEvent(GameEvent.BLOCK_CHANGE, pos, GameEvent.Context.of(player, picked));
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
