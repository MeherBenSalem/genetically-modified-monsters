package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.ShamblerAnimations;
import com.nightbeam.sporeandstem.entity.ShamblerEntity;
import net.minecraft.client.model.geom.ModelPart;

public class ShamblerModel extends RigModel<ShamblerEntity> {
    private final ModelPart head;

    public ShamblerModel(ModelPart root) {
        super(root);
        this.head = part("head");
    }

    @Override
    public void setupAnim(ShamblerEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        resetPose();
        this.animateWalk(ShamblerAnimations.WALK, limbSwing, limbSwingAmount, 2.0F, 2.5F);
        CreatureAnim.loop(this, ShamblerAnimations.IDLE, ageInTicks, 1.0F, 1.0F - Math.min(1.0F, limbSwingAmount * 2.0F) * 0.5F);
        this.animate(entity.attackState, ShamblerAnimations.ATTACK, ageInTicks);
        this.animate(entity.riseState, ShamblerAnimations.RISE, ageInTicks);
        if (!entity.isRising()) {
            look(head, netHeadYaw, headPitch, 45.0F, 30.0F);
        }
    }
}
