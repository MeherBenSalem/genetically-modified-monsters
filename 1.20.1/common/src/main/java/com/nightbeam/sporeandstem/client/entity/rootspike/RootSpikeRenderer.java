package com.nightbeam.sporeandstem.client.entity.rootspike;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.entity.RootSpikeEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

/** Draws a Root Spike once it has broken through, with its glowing veins at full brightness. */
public class RootSpikeRenderer extends EntityRenderer<RootSpikeEntity> {
    private static final ResourceLocation TEXTURE = SporeAndStem.id("textures/entity/root_spike/root_spike.png");
    private static final ResourceLocation GLOW = SporeAndStem.id("textures/entity/root_spike/root_spike_glow.png");
    private final RootSpikeModel model;

    public RootSpikeRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.model = new RootSpikeModel(context.bakeLayer(RootSpikeModel.LAYER));
    }

    @Override
    public void render(RootSpikeEntity entity, float yaw, float partialTick, PoseStack poseStack, MultiBufferSource buffers,
                       int packedLight) {
        if (!entity.hasErupted()) {
            return;
        }
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(90.0F - entity.getYRot()));
        poseStack.scale(-1.0F, -1.0F, 1.0F);
        poseStack.translate(0.0F, -1.501F, 0.0F);
        this.model.setupAnim(entity, 0.0F, 0.0F, entity.tickCount + partialTick, 0.0F, 0.0F);
        this.model.renderToBuffer(poseStack, buffers.getBuffer(this.model.renderType(TEXTURE)), packedLight,
                OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F);
        this.model.renderToBuffer(poseStack, buffers.getBuffer(RenderType.eyes(GLOW)), 0xF00000, OverlayTexture.NO_OVERLAY,
                1.0F, 1.0F, 1.0F, 1.0F);
        poseStack.popPose();
        super.render(entity, yaw, partialTick, poseStack, buffers, packedLight);
    }

    @Override
    public ResourceLocation getTextureLocation(RootSpikeEntity entity) {
        return TEXTURE;
    }
}
