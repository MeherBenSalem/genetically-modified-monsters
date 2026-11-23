package com.nightbeam.sporeandstem.client.entity.creature;

import com.mojang.blaze3d.vertex.PoseStack;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderer;
import com.nightbeam.sporeandstem.entity.TrufflerEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.Identifier;

public class TrufflerRenderer extends CreatureRenderer<TrufflerEntity, TrufflerModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("truffler"), "main");
    private static final Identifier TEXTURE = SporeAndStem.id("textures/entity/truffler/truffler.png");

    public TrufflerRenderer(EntityRendererProvider.Context context) {
        super(context, new TrufflerModel(context.bakeLayer(LAYER)), 0.6F);
    }

    @Override
    protected Identifier texture(TrufflerEntity entity) {
        return TEXTURE;
    }

    @Override
    protected void scale(CreatureRenderState<TrufflerEntity> state, PoseStack poseStack) {
        if (state.isBaby) {
            poseStack.scale(0.5F, 0.5F, 0.5F);
        }
    }
}
