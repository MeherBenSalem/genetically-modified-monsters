package com.nightbeam.sporeandstem.content;

import com.nightbeam.sporeandstem.SporeAndStem;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.block.state.properties.WoodType;
import net.minecraft.world.level.material.MapColor;

/**
 * The three huge fungi that give a full wood set. Sounds follow the nether stems: soft, fibrous, fireproof.
 * The set and wood types only carry sounds here (doors, gates); they are not registered because the mod has no signs.
 */
public enum FungusWood {
    GLOWCAP("glowcap", MapColor.COLOR_LIGHT_BLUE, MapColor.TERRACOTTA_WHITE, MapColor.COLOR_CYAN),
    BOUNCECAP("bouncecap", MapColor.TERRACOTTA_PINK, MapColor.TERRACOTTA_WHITE, MapColor.COLOR_PINK),
    INKCAP("inkcap", MapColor.TERRACOTTA_BLACK, MapColor.TERRACOTTA_GRAY, MapColor.COLOR_GRAY);

    private final String id;
    private final MapColor planks;
    private final MapColor stem;
    private final MapColor cap;
    private final BlockSetType setType;
    private final WoodType woodType;

    FungusWood(String id, MapColor planks, MapColor stem, MapColor cap) {
        this.id = id;
        this.planks = planks;
        this.stem = stem;
        this.cap = cap;
        String name = SporeAndStem.MOD_ID + ":" + id;
        this.setType = new BlockSetType(name, true, SoundType.NETHER_WOOD,
                SoundEvents.NETHER_WOOD_DOOR_CLOSE, SoundEvents.NETHER_WOOD_DOOR_OPEN,
                SoundEvents.NETHER_WOOD_TRAPDOOR_CLOSE, SoundEvents.NETHER_WOOD_TRAPDOOR_OPEN,
                SoundEvents.NETHER_WOOD_PRESSURE_PLATE_CLICK_OFF, SoundEvents.NETHER_WOOD_PRESSURE_PLATE_CLICK_ON,
                SoundEvents.NETHER_WOOD_BUTTON_CLICK_OFF, SoundEvents.NETHER_WOOD_BUTTON_CLICK_ON);
        this.woodType = new WoodType(name, this.setType, SoundType.NETHER_WOOD,
                SoundType.NETHER_WOOD_HANGING_SIGN, SoundEvents.NETHER_WOOD_FENCE_GATE_CLOSE,
                SoundEvents.NETHER_WOOD_FENCE_GATE_OPEN);
    }

    public String id() {
        return id;
    }

    public MapColor planksColor() {
        return planks;
    }

    public MapColor stemColor() {
        return stem;
    }

    public MapColor capColor() {
        return cap;
    }

    public BlockSetType setType() {
        return setType;
    }

    public WoodType woodType() {
        return woodType;
    }
}
