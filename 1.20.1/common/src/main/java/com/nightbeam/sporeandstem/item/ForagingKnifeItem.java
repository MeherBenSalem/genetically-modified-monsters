package com.nightbeam.sporeandstem.item;

import com.nightbeam.sporeandstem.registry.ModTags;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.Tiers;

/**
 * A forager's knife. Mines fungal blocks fast; small fungi and caps cut with it drop one extra, and it harvests
 * Mycelial Thread from veils (both through the loot tables, which check {@code #spore_and_stem:foraging_tools}).
 */
public class ForagingKnifeItem extends DiggerItem {

    public ForagingKnifeItem(Properties properties) {
        // 1 base + 2 iron bonus = 3 attack damage, 2.0 attack speed.
        super(0.0F, -2.0F, Tiers.IRON, ModTags.Blocks.MINEABLE_WITH_KNIFE, properties);
    }
}
