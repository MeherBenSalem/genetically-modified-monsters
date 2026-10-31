package com.nightbeam.sporeandstem.block;

import net.minecraft.world.level.block.ButtonBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.PressurePlateBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockSetType;

/** Public constructors for the wood-set blocks whose vanilla constructors are protected. */
public final class WoodBlocks {

    private WoodBlocks() {
    }

    public static class Stairs extends StairBlock {
        public Stairs(BlockState base, Properties properties) {
            super(base, properties);
        }
    }

    public static class Door extends DoorBlock {
        public Door(BlockSetType type, Properties properties) {
            super(properties, type);
        }
    }

    public static class Trapdoor extends TrapDoorBlock {
        public Trapdoor(BlockSetType type, Properties properties) {
            super(properties, type);
        }
    }

    public static class Button extends ButtonBlock {
        public Button(BlockSetType type, int ticksToStayPressed, Properties properties) {
            super(properties, type, ticksToStayPressed, true); // wooden: arrows press it
        }
    }

    public static class PressurePlate extends PressurePlateBlock {
        public PressurePlate(BlockSetType type, Properties properties) {
            super(Sensitivity.EVERYTHING, properties, type);
        }
    }
}
