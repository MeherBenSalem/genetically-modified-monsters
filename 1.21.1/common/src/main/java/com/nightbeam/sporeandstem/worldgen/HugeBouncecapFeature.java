package com.nightbeam.sporeandstem.worldgen;

import com.mojang.serialization.Codec;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.state.BlockState;

/**
 * A Huge Bouncecap: a short, stout stem that flares at the foot, under a round, puffy dome closed underneath like a
 * bun. The dome is a shell; its underside layer is solid so it reads as one soft mass.
 */
public class HugeBouncecapFeature extends HugeFungusFeature {

    public HugeBouncecapFeature(Codec<HugeFungusConfiguration> codec) {
        super(codec);
    }

    @Override
    protected void shape(FungusPlan plan, RandomSource random, int height, int radius) {
        // A stout, plus-shaped stem that narrows to a single block just under the dome, with root feet at its base.
        for (int y = 0; y < height; y++) {
            plan.stem(0, y, 0);
            if (y < height - 1) {
                for (Direction side : Direction.Plane.HORIZONTAL) {
                    plan.stem(side.getStepX(), y, side.getStepZ());
                }
            }
        }
        for (Direction side : Direction.Plane.HORIZONTAL) {
            if (random.nextFloat() < 0.6F) {
                plan.stem(side.getStepX() * 2, 0, side.getStepZ() * 2);
            }
        }
        double a = radius + 0.5;
        double b = radius * 0.9 + 0.6;
        int yc = height + 1;
        int reach = radius + 1;
        int topY = yc + (int) Math.ceil(b);
        for (int y = height; y <= topY; y++) {
            for (int dx = -reach; dx <= reach; dx++) {
                for (int dz = -reach; dz <= reach; dz++) {
                    if (!inside(dx, y - yc, dz, a, b)) {
                        continue;
                    }
                    boolean shell = y == height
                            || !inside(dx + 1, y - yc, dz, a, b) || !inside(dx - 1, y - yc, dz, a, b)
                            || !inside(dx, y - yc + 1, dz, a, b) || !inside(dx, y - yc - 1, dz, a, b)
                            || !inside(dx, y - yc, dz + 1, a, b) || !inside(dx, y - yc, dz - 1, a, b);
                    if (shell) {
                        plan.cap(dx, y, dz);
                    }
                }
            }
        }
    }

    private static boolean inside(int dx, int dy, int dz, double a, double b) {
        return (dx * dx + dz * dz) / (a * a) + (dy * dy) / (b * b) <= 1.0;
    }

    @Override
    protected BlockState stem() {
        return ModBlocks.BOUNCECAP_WOOD.stem().get().defaultBlockState();
    }

    @Override
    protected BlockState cap() {
        return ModBlocks.BOUNCECAP_CAP.get().defaultBlockState();
    }
}
