package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.SporemawAnimations;
import com.nightbeam.sporeandstem.entity.SporemawEntity;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.geom.ModelPart;

public class SporemawModel extends RigModel<SporemawEntity> {
    private final ModelPart head;
    private final KeyframeAnimation burrowed;
    private final KeyframeAnimation emerge;
    private final KeyframeAnimation burrow;
    private final KeyframeAnimation idle;
    private final KeyframeAnimation spit;

    public SporemawModel(ModelPart root) {
        super(root);
        this.head = part("head");
        this.burrowed = bake(SporemawAnimations.BURROWED);
        this.emerge = bake(SporemawAnimations.EMERGE);
        this.burrow = bake(SporemawAnimations.BURROW);
        this.idle = bake(SporemawAnimations.IDLE);
        this.spit = bake(SporemawAnimations.SPIT);
    }

    @Override
    protected void animate(SporemawEntity entity, CreatureRenderState<SporemawEntity> state, float limbSwing,
                           float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        switch (entity.getState()) {
            case SporemawEntity.BURROWED -> CreatureAnim.loop(this.burrowed, ageInTicks);
            case SporemawEntity.EMERGING -> this.emerge.apply(entity.emergeState, ageInTicks);
            case SporemawEntity.BURROWING -> this.burrow.apply(entity.burrowState, ageInTicks);
            default -> {
                CreatureAnim.loop(this.idle, ageInTicks);
                this.spit.apply(entity.spitState, ageInTicks);
                look(head, netHeadYaw, headPitch, 30.0F, 20.0F);
            }
        }
    }
}
