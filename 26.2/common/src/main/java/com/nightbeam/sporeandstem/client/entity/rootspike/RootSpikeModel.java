package com.nightbeam.sporeandstem.client.entity.rootspike;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.RootSpikeAnimations;
import com.nightbeam.sporeandstem.entity.RootSpikeEntity;
import net.minecraft.client.animation.KeyframeAnimation;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;

/** Root Spike: geometry and animation come from tools/assets/ss/entities/root_spike.py. */
public class RootSpikeModel extends RigModel<RootSpikeEntity> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("root_spike"), "main");
    private final KeyframeAnimation erupt;

    public RootSpikeModel(ModelPart root) {
        super(root);
        this.erupt = bake(RootSpikeAnimations.ERUPT);
    }

    @Override
    protected void animate(RootSpikeEntity entity, CreatureRenderState<RootSpikeEntity> state, float limbSwing,
                           float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.erupt.apply(entity.eruptState, ageInTicks);
    }
}
