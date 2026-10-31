package com.nightbeam.sporeandstem.client.entity;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FastColor;
import net.minecraft.world.entity.LivingEntity;

import java.util.function.Function;
import java.util.function.ToDoubleFunction;

/**
 * Draws a creature's emissive texture at full brightness (additive, like eyes): black texels add nothing. The
 * texture and its strength (0-1, e.g. to pulse or fade) come from the entity.
 */
public class GlowLayer<T extends LivingEntity, M extends EntityModel<T>> extends RenderLayer<T, M> {
    private final Function<T, ResourceLocation> texture;
    private final ToDoubleFunction<T> strength;

    public GlowLayer(RenderLayerParent<T, M> parent, Function<T, ResourceLocation> texture, ToDoubleFunction<T> strength) {
        super(parent);
        this.texture = texture;
        this.strength = strength;
    }

    public GlowLayer(RenderLayerParent<T, M> parent, ResourceLocation texture) {
        this(parent, entity -> texture, entity -> 1.0);
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource buffers, int packedLight, T entity, float limbSwing,
                       float limbSwingAmount, float partialTick, float ageInTicks, float netHeadYaw, float headPitch) {
        float s = (float) Math.max(0.0, Math.min(1.0, strength.applyAsDouble(entity)));
        if (s <= 0.0F || entity.isInvisible()) {
            return;
        }
        VertexConsumer consumer = buffers.getBuffer(RenderType.eyes(texture.apply(entity)));
        int c = Math.round(s * 255.0F);
        this.getParentModel().renderToBuffer(poseStack, consumer, 0xF00000, OverlayTexture.NO_OVERLAY,
                FastColor.ARGB32.color(255, c, c, c));
    }
}
