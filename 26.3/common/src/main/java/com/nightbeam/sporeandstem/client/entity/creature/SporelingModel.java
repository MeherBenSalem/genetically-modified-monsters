package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.SporelingAnimations;
import com.nightbeam.sporeandstem.entity.SporelingEntity;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class SporelingModel extends RigModel<SporelingEntity> {
    private final ModelPart cap;
    private final KeyframeAnimation sit;
    private final KeyframeAnimation walk;
    private final KeyframeAnimation idle;
    private final KeyframeAnimation sneeze;
    private final KeyframeAnimation happy;

    public SporelingModel(ModelPart root) {
        super(root);
        this.cap = part("cap");
        this.sit = bake(SporelingAnimations.SIT);
        this.walk = bake(SporelingAnimations.WALK);
        this.idle = bake(SporelingAnimations.IDLE);
        this.sneeze = bake(SporelingAnimations.SNEEZE);
        this.happy = bake(SporelingAnimations.HAPPY);
    }

    @Override
    protected void animate(SporelingEntity entity, CreatureRenderState<SporelingEntity> state, float limbSwing,
                           float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity.isInSittingPose()) {
            CreatureAnim.loop(this.sit, ageInTicks);
        } else {
            this.walk.applyWalk(limbSwing, limbSwingAmount, 3.0F, 2.5F);
            CreatureAnim.loop(this.idle, ageInTicks, 1.0F, 1.0F - Math.min(1.0F, limbSwingAmount * 2.0F) * 0.6F);
        }
        this.sneeze.apply(entity.sneezeState, ageInTicks);
        this.happy.apply(entity.happyState, ageInTicks);
        // The whole cap is its "head": it turns a little toward what it looks at.
        cap.yRot += Mth.clamp(netHeadYaw, -40.0F, 40.0F) * Mth.DEG_TO_RAD * 0.5F;
        cap.xRot += Mth.clamp(headPitch, -20.0F, 20.0F) * Mth.DEG_TO_RAD * 0.4F;
    }
}
