package com.nightbeam.sporeandstem.content;

import com.nightbeam.sporeandstem.registry.ModBlocks;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.util.function.Supplier;

/** What a Cultivation Log can be inoculated with. NONE is a fresh log. */
public enum CultivationFungus implements StringRepresentable {
    NONE("none", () -> null),
    GLOWCAP("glowcap", () -> ModBlocks.GLOWCAP.get().asItem()),
    BOUNCECAP("bouncecap", () -> ModBlocks.BOUNCECAP.get().asItem()),
    INKCAP("inkcap", () -> ModBlocks.INKCAP.get().asItem()),
    MOREL("morel", () -> ModBlocks.MOREL.get().asItem()),
    CHANTERELLE("chanterelle", () -> ModBlocks.CHANTERELLE.get().asItem()),
    FROSTCAP("frostcap", () -> ModBlocks.FROSTCAP.get().asItem()),
    EMBERSTOOL("emberstool", () -> ModBlocks.EMBERSTOOL.get().asItem());

    private final String name;
    private final Supplier<Item> item;

    CultivationFungus(String name, Supplier<Item> item) {
        this.name = name;
        this.item = item;
    }

    public Item item() {
        return item.get();
    }

    /** The fungus this stack inoculates a log with, or NONE. */
    public static CultivationFungus of(ItemStack stack) {
        for (CultivationFungus fungus : values()) {
            if (fungus != NONE && stack.is(fungus.item())) {
                return fungus;
            }
        }
        return NONE;
    }

    @Override
    public String getSerializedName() {
        return name;
    }
}
