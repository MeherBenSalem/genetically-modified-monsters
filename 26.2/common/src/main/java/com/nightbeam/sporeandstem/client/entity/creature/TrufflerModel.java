package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.TrufflerAnimations;
import com.nightbeam.sporeandstem.entity.TrufflerEntity;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.geom.ModelPart;

public class TrufflerModel extends RigModel<TrufflerEntity> {
    private final ModelPart head;
    private final KeyframeAnimation walk;
    private final KeyframeAnimation idle;
    private final KeyframeAnimation sniff;
    private final KeyframeAnimation dig;

    public TrufflerModel(ModelPart root) {
        super(root);
        this.head = part("head");
        this.walk = bake(TrufflerAnimations.WALK);
        this.idle = bake(TrufflerAnimations.IDLE);
        this.sniff = bake(TrufflerAnimations.SNIFF);
        this.dig = bake(TrufflerAnimations.DIG);
    }

    @Override
    protected void animate(TrufflerEntity entity, CreatureRenderState<TrufflerEntity> state, float limbSwing,
                           float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.walk.applyWalk(limbSwing, limbSwingAmount, 2.5F, 2.5F);
        CreatureAnim.loop(this.idle, ageInTicks + entity.getId() * 7.0F);
        boolean busy = entity.sniffState.isStarted() && entity.sniffState.getTimeInMillis(ageInTicks) < 1400L
                || entity.digState.isStarted() && entity.digState.getTimeInMillis(ageInTicks) < 1600L;
        this.sniff.apply(entity.sniffState, ageInTicks);
        this.dig.apply(entity.digState, ageInTicks);
        if (!busy) {
            look(head, netHeadYaw, headPitch, 35.0F, 25.0F);
        }
    }
}
