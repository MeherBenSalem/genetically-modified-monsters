package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.BloatshroomAnimations;
import com.nightbeam.sporeandstem.entity.BloatshroomEntity;
import net.minecraft.client.model.geom.ModelPart;

public class BloatshroomModel extends RigModel<BloatshroomEntity> {

    public BloatshroomModel(ModelPart root) {
        super(root);
    }

    @Override
    public void setupAnim(BloatshroomEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        resetPose();
        float swell = entity.getSwelling(ageInTicks - entity.tickCount);
        this.animateWalk(BloatshroomAnimations.WALK, limbSwing, limbSwingAmount, 3.0F, 2.5F);
        CreatureAnim.loop(this, BloatshroomAnimations.IDLE, ageInTicks, 1.0F, 1.0F - Math.min(1.0F, swell * 2.0F));
        if (swell > 0.0F) {
            CreatureAnim.at(this, BloatshroomAnimations.SWELL, swell, 1.0F);
        }
    }
}
