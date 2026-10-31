package com.nightbeam.sporeandstem.client.entity.myceliarch;

import com.mojang.blaze3d.vertex.PoseStack;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.MyceliarchEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/**
 * Draws the Myceliarch with its emissive gills, veins and eyes: a slow pulse in the first bloom, full and with more
 * veins in the second, fading as it dies. It does not topple over on death (its own collapse animation plays) and
 * casts no shadow while it is still underground.
 */
public class MyceliarchRenderer extends MobRenderer<MyceliarchEntity, MyceliarchModel> {
    private static final ResourceLocation TEXTURE = SporeAndStem.id("textures/entity/myceliarch/myceliarch.png");
    private static final ResourceLocation GLOW = SporeAndStem.id("textures/entity/myceliarch/myceliarch_glow.png");
    private static final ResourceLocation BLOOM_GLOW = SporeAndStem.id("textures/entity/myceliarch/myceliarch_bloom_glow.png");
    private static final float SHADOW = 1.6F;

    public MyceliarchRenderer(EntityRendererProvider.Context context) {
        super(context, new MyceliarchModel(context.bakeLayer(MyceliarchModel.LAYER)), SHADOW);
        this.addLayer(new GlowLayer<>(this, e -> e.isBloom() ? BLOOM_GLOW : GLOW, MyceliarchRenderer::glow));
    }

    private static double glow(MyceliarchEntity entity) {
        int collapse = entity.getCollapseTicks();
        float fade = collapse > 0 ? Math.max(0.0F, 1.0F - collapse / 55.0F) : 1.0F;
        if (entity.isBloom()) {
            return (0.9 + 0.1 * Mth.sin(entity.tickCount * 0.35F)) * fade;
        }
        return (0.7 + 0.15 * Mth.sin(entity.tickCount * 0.08F)) * fade;
    }

    @Override
    public ResourceLocation getTextureLocation(MyceliarchEntity entity) {
        return TEXTURE;
    }

    @Override
    public void render(MyceliarchEntity entity, float yaw, float partialTick, PoseStack poseStack, MultiBufferSource buffers,
                       int packedLight) {
        float underground = 0.0F;
        if (entity.isEmerging() && entity.emergeState.isStarted()) {
            float t = entity.emergeState.getAccumulatedTime() / 1000.0F;
            underground = t < 3.4F ? 1.0F : Math.max(0.0F, 1.0F - (t - 3.4F) / 1.2F);
        }
        int collapse = entity.getCollapseTicks();
        float sinking = collapse > 30 ? Math.min(1.0F, (collapse - 30) / 25.0F) : 0.0F;
        this.shadowRadius = SHADOW * (1.0F - Math.max(underground, sinking));
        super.render(entity, yaw, partialTick, poseStack, buffers, packedLight);
    }

    @Override
    protected float getFlipDegrees(MyceliarchEntity entity) {
        return 0.0F;
    }
}
