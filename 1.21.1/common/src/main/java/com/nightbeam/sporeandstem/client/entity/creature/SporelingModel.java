package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.SporelingAnimations;
import com.nightbeam.sporeandstem.entity.SporelingEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class SporelingModel extends RigModel<SporelingEntity> {
    private final ModelPart cap;

    public SporelingModel(ModelPart root) {
        super(root);
        this.cap = part("cap");
    }

    @Override
    public void setupAnim(SporelingEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        resetPose();
        if (entity.isInSittingPose()) {
            CreatureAnim.loop(this, SporelingAnimations.SIT, ageInTicks);
        } else {
            this.animateWalk(SporelingAnimations.WALK, limbSwing, limbSwingAmount, 3.0F, 2.5F);
            CreatureAnim.loop(this, SporelingAnimations.IDLE, ageInTicks, 1.0F, 1.0F - Math.min(1.0F, limbSwingAmount * 2.0F) * 0.6F);
        }
        this.animate(entity.sneezeState, SporelingAnimations.SNEEZE, ageInTicks);
        this.animate(entity.happyState, SporelingAnimations.HAPPY, ageInTicks);
        // The whole cap is its "head": it turns a little toward what it looks at.
        cap.yRot += Mth.clamp(netHeadYaw, -40.0F, 40.0F) * Mth.DEG_TO_RAD * 0.5F;
        cap.xRot += Mth.clamp(headPitch, -20.0F, 20.0F) * Mth.DEG_TO_RAD * 0.4F;
    }
}
