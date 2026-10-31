package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.effect.MycosisEffect;
import com.nightbeam.sporeandstem.effect.SimpleEffect;
import com.nightbeam.sporeandstem.platform.Services;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

public final class ModEffects {
    public static final RegistryEntry<MobEffect> MYCOSIS = Services.REGISTRAR.register(Registries.MOB_EFFECT, "mycosis",
            MycosisEffect::new);
    public static final RegistryEntry<MobEffect> SPORE_WARD = Services.REGISTRAR.register(Registries.MOB_EFFECT, "spore_ward",
            () -> new SimpleEffect(MobEffectCategory.BENEFICIAL, 0xD9C9A3));
    public static final RegistryEntry<MobEffect> ROOTED = Services.REGISTRAR.register(Registries.MOB_EFFECT, "rooted",
            () -> new SimpleEffect(MobEffectCategory.HARMFUL, 0x6B4F2A)
                    .addAttributeModifier(Attributes.MOVEMENT_SPEED, "a7d4c1f2-3b5e-4c8a-9f61-2e0b7d9c4a18", -0.6,
                            AttributeModifier.Operation.MULTIPLY_TOTAL));
    // Rooted also stops jumping: 1.20.1 has no jump attribute for players, so LivingEntityMixin zeroes the jump.

    private ModEffects() {
    }

    public static void init() {
    }
}
