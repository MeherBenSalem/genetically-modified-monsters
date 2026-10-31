package com.nightbeam.sporeandstem.client.entity.rootspike;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.RootSpikeAnimations;
import com.nightbeam.sporeandstem.entity.RootSpikeEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;

/** Root Spike: geometry and animation come from tools/assets/ss/entities/root_spike.py. */
public class RootSpikeModel extends RigModel<RootSpikeEntity> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("root_spike"), "main");

    public RootSpikeModel(ModelPart root) {
        super(root);
    }

    @Override
    public void setupAnim(RootSpikeEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks,
                          float netHeadYaw, float headPitch) {
        resetPose();
        this.animate(entity.eruptState, RootSpikeAnimations.ERUPT, ageInTicks);
    }
}
