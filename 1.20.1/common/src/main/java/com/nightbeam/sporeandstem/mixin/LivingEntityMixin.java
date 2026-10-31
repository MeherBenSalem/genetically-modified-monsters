package com.nightbeam.sporeandstem.mixin;

import com.nightbeam.sporeandstem.effect.MycosisEffect;
import com.nightbeam.sporeandstem.registry.ModEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Two effect hooks that 1.21 has built in: an effect hearing that its carrier was removed (Mycosis rising) and a jump
 * attribute (Rooted).
 */
@Mixin(LivingEntity.class)
public abstract class LivingEntityMixin {

    @Inject(method = "remove", at = @At("HEAD"))
    private void spore_and_stem$mycosisRising(Entity.RemovalReason reason, CallbackInfo ci) {
        LivingEntity self = (LivingEntity) (Object) this;
        if (!self.level().isClientSide && self.hasEffect(ModEffects.MYCOSIS.get())) {
            MycosisEffect.onRemoved(self, reason);
        }
    }

    @Inject(method = "getJumpPower", at = @At("RETURN"), cancellable = true)
    private void spore_and_stem$rootedNoJump(CallbackInfoReturnable<Float> cir) {
        if (((LivingEntity) (Object) this).hasEffect(ModEffects.ROOTED.get())) {
            cir.setReturnValue(0.0F);
        }
    }
}
