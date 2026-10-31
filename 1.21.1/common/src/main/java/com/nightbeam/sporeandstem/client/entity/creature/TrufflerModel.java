package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.TrufflerAnimations;
import com.nightbeam.sporeandstem.entity.TrufflerEntity;
import net.minecraft.client.model.geom.ModelPart;

public class TrufflerModel extends RigModel<TrufflerEntity> {
    private final ModelPart head;

    public TrufflerModel(ModelPart root) {
        super(root);
        this.head = part("head");
    }

    @Override
    public void setupAnim(TrufflerEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        resetPose();
        this.animateWalk(TrufflerAnimations.WALK, limbSwing, limbSwingAmount, 2.5F, 2.5F);
        CreatureAnim.loop(this, TrufflerAnimations.IDLE, ageInTicks + entity.getId() * 7.0F);
        boolean busy = entity.sniffState.isStarted() && entity.sniffState.getAccumulatedTime() < 1400L
                || entity.digState.isStarted() && entity.digState.getAccumulatedTime() < 1600L;
        this.animate(entity.sniffState, TrufflerAnimations.SNIFF, ageInTicks);
        this.animate(entity.digState, TrufflerAnimations.DIG, ageInTicks);
        if (!busy) {
            look(head, netHeadYaw, headPitch, 35.0F, 25.0F);
        }
    }
}
