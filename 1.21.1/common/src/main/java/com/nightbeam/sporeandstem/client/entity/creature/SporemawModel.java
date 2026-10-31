package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.SporemawAnimations;
import com.nightbeam.sporeandstem.entity.SporemawEntity;
import net.minecraft.client.model.geom.ModelPart;

public class SporemawModel extends RigModel<SporemawEntity> {
    private final ModelPart head;

    public SporemawModel(ModelPart root) {
        super(root);
        this.head = part("head");
    }

    @Override
    public void setupAnim(SporemawEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        resetPose();
        switch (entity.getState()) {
            case SporemawEntity.BURROWED -> CreatureAnim.loop(this, SporemawAnimations.BURROWED, ageInTicks);
            case SporemawEntity.EMERGING -> this.animate(entity.emergeState, SporemawAnimations.EMERGE, ageInTicks);
            case SporemawEntity.BURROWING -> this.animate(entity.burrowState, SporemawAnimations.BURROW, ageInTicks);
            default -> {
                CreatureAnim.loop(this, SporemawAnimations.IDLE, ageInTicks);
                this.animate(entity.spitState, SporemawAnimations.SPIT, ageInTicks);
                look(head, netHeadYaw, headPitch, 30.0F, 20.0F);
            }
        }
    }
}
