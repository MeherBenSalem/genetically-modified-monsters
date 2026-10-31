package com.nightbeam.sporeandstem.client.entity.creature;

import com.mojang.blaze3d.vertex.PoseStack;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.entity.TrufflerEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;

public class TrufflerRenderer extends MobRenderer<TrufflerEntity, TrufflerModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("truffler"), "main");
    private static final ResourceLocation TEXTURE = SporeAndStem.id("textures/entity/truffler/truffler.png");

    public TrufflerRenderer(EntityRendererProvider.Context context) {
        super(context, new TrufflerModel(context.bakeLayer(LAYER)), 0.6F);
    }

    @Override
    public ResourceLocation getTextureLocation(TrufflerEntity entity) {
        return TEXTURE;
    }

    @Override
    protected void scale(TrufflerEntity entity, PoseStack poseStack, float partialTick) {
        if (entity.isBaby()) {
            poseStack.scale(0.5F, 0.5F, 0.5F);
        }
    }
}
