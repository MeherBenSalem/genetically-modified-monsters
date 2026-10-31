package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.MimicapAnimations;
import com.nightbeam.sporeandstem.entity.MimicapEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class MimicapModel extends RigModel<MimicapEntity> {
    private final ModelPart cap;

    public MimicapModel(ModelPart root) {
        super(root);
        this.cap = part("cap");
    }

    @Override
    public void setupAnim(MimicapEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        resetPose();
        switch (entity.getPhase()) {
            case MimicapEntity.HIDDEN -> CreatureAnim.loop(this, MimicapAnimations.HIDDEN, ageInTicks);
            case MimicapEntity.WAKING -> this.animate(entity.wakeState, MimicapAnimations.WAKE, ageInTicks);
            case MimicapEntity.SETTLING -> this.animate(entity.settleState, MimicapAnimations.SETTLE, ageInTicks);
            default -> {
                this.animateWalk(MimicapAnimations.WALK, limbSwing, limbSwingAmount, 4.0F, 2.0F);
                CreatureAnim.loop(this, MimicapAnimations.IDLE, ageInTicks, 1.0F, 1.0F - Math.min(1.0F, limbSwingAmount * 3.0F));
                this.animate(entity.biteState, MimicapAnimations.BITE, ageInTicks);
                cap.yRot += Mth.clamp(netHeadYaw, -25.0F, 25.0F) * Mth.DEG_TO_RAD * 0.4F;
            }
        }
    }
}
