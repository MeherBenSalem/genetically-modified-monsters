package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ToolMaterial;

/**
 * A forager's knife. Mines fungal blocks fast; small fungi and caps cut with it drop one extra, and it harvests
 * Mycelial Thread from veils (both through the loot tables, which check {@code #spore_and_stem:foraging_tools}).
 * Since 1.21.2 a tool is a plain item with a tool component, so this only builds the properties.
 */
public final class ForagingKnifeItem {

    private ForagingKnifeItem() {
    }

    public static Item.Properties properties(Item.Properties properties) {
        return properties.tool(ToolMaterial.IRON, ModTags.Blocks.MINEABLE_WITH_KNIFE, 0.0F, -2.0F, 0.0F);
    }
}
