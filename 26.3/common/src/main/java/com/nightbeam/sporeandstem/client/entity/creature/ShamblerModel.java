package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.ShamblerAnimations;
import com.nightbeam.sporeandstem.entity.ShamblerEntity;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.geom.ModelPart;

public class ShamblerModel extends RigModel<ShamblerEntity> {
    private final ModelPart head;
    private final KeyframeAnimation walk;
    private final KeyframeAnimation idle;
    private final KeyframeAnimation attack;
    private final KeyframeAnimation rise;

    public ShamblerModel(ModelPart root) {
        super(root);
        this.head = part("head");
        this.walk = bake(ShamblerAnimations.WALK);
        this.idle = bake(ShamblerAnimations.IDLE);
        this.attack = bake(ShamblerAnimations.ATTACK);
        this.rise = bake(ShamblerAnimations.RISE);
    }

    @Override
    protected void animate(ShamblerEntity entity, CreatureRenderState<ShamblerEntity> state, float limbSwing,
                           float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.walk.applyWalk(limbSwing, limbSwingAmount, 2.0F, 2.5F);
        CreatureAnim.loop(this.idle, ageInTicks, 1.0F, 1.0F - Math.min(1.0F, limbSwingAmount * 2.0F) * 0.5F);
        this.attack.apply(entity.attackState, ageInTicks);
        this.rise.apply(entity.riseState, ageInTicks);
        if (!entity.isRising()) {
            look(head, netHeadYaw, headPitch, 45.0F, 30.0F);
        }
    }
}
