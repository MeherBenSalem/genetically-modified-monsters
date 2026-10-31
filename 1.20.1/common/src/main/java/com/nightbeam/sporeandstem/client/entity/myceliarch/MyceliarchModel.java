package com.nightbeam.sporeandstem.client.entity.myceliarch;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.MyceliarchAnimations;
import com.nightbeam.sporeandstem.entity.MyceliarchEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;

/** The Myceliarch: geometry and animations come from tools/assets/ss/entities/myceliarch.py. */
public class MyceliarchModel extends RigModel<MyceliarchEntity> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("myceliarch"), "main");
    private final ModelPart head;

    public MyceliarchModel(ModelPart root) {
        super(root);
        this.head = part("head");
    }

    @Override
    public void setupAnim(MyceliarchEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks,
                          float netHeadYaw, float headPitch) {
        resetPose();
        boolean free = entity.getState() == MyceliarchEntity.IDLE && entity.getCollapseTicks() == 0;
        if (free) {
            look(this.head, netHeadYaw * 0.6F, headPitch * 0.6F, 35.0F, 25.0F);
            this.animateWalk(MyceliarchAnimations.WALK, limbSwing, limbSwingAmount, 2.0F, 2.2F);
        }
        this.animate(entity.idleState, MyceliarchAnimations.IDLE, ageInTicks);
        this.animate(entity.emergeState, MyceliarchAnimations.EMERGE, ageInTicks);
        this.animate(entity.slamState, MyceliarchAnimations.SLAM, ageInTicks);
        this.animate(entity.eruptState, MyceliarchAnimations.ERUPT, ageInTicks);
        this.animate(entity.novaState, MyceliarchAnimations.NOVA, ageInTicks);
        this.animate(entity.broodState, MyceliarchAnimations.BROOD, ageInTicks);
        this.animate(entity.roarState, MyceliarchAnimations.ROAR, ageInTicks);
        this.animate(entity.rainState, MyceliarchAnimations.RAIN, ageInTicks);
        this.animate(entity.deathState, MyceliarchAnimations.DEATH, ageInTicks);
    }
}
