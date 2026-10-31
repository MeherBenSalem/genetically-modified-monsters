package com.nightbeam.sporeandstem.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;

/** A plain effect whose behaviour lives in attribute modifiers or in code that checks for it (Spore Ward, Rooted). */
public class SimpleEffect extends MobEffect {

    public SimpleEffect(MobEffectCategory category, int color) {
        super(category, color);
    }
}
