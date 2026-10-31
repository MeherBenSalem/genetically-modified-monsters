package com.nightbeam.sporeandstem.client.entity;

import net.minecraft.client.animation.AnimationDefinition;
import net.minecraft.client.animation.KeyframeAnimations;
import net.minecraft.client.model.HierarchicalModel;
import org.joml.Vector3f;

/** Plays keyframed animations outside an AnimationState: looping by age, or at an exact progress. */
public final class CreatureAnim {
    private static final Vector3f CACHE = new Vector3f();

    private CreatureAnim() {
    }

    /** A looping animation driven by the entity's age (ticks, partial included). */
    public static void loop(HierarchicalModel<?> model, AnimationDefinition definition, float ageInTicks) {
        loop(model, definition, ageInTicks, 1.0F, 1.0F);
    }

    /** As {@link #loop(HierarchicalModel, AnimationDefinition, float)}, with a playback speed and a blend weight. */
    public static void loop(HierarchicalModel<?> model, AnimationDefinition definition, float ageInTicks, float speed,
                            float weight) {
        if (weight <= 0.001F) {
            return;
        }
        long millis = (long) (ageInTicks * 50.0F * speed);
        KeyframeAnimations.animate(model, definition, millis, weight, CACHE);
    }

    /** A one-shot animation at progress 0..1 of its length (e.g. a swell driven by synced progress). */
    public static void at(HierarchicalModel<?> model, AnimationDefinition definition, float progress, float weight) {
        if (weight <= 0.001F) {
            return;
        }
        long millis = (long) (Math.max(0.0F, Math.min(1.0F, progress)) * definition.lengthInSeconds() * 1000.0F);
        KeyframeAnimations.animate(model, definition, millis, weight, CACHE);
    }
}
