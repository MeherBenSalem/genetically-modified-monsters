package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.SporemawEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class SporemawRenderer extends MobRenderer<SporemawEntity, SporemawModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("sporemaw"), "main");
    private static final ResourceLocation TEXTURE = SporeAndStem.id("textures/entity/sporemaw/sporemaw.png");
    private static final ResourceLocation GLOW = SporeAndStem.id("textures/entity/sporemaw/sporemaw_glow.png");

    public SporemawRenderer(EntityRendererProvider.Context context) {
        super(context, new SporemawModel(context.bakeLayer(LAYER)), 0.55F);
        this.addLayer(new GlowLayer<>(this, e -> GLOW, e -> e.getState() == SporemawEntity.BURROWED ? 0.35
                : 0.8 + 0.2 * Mth.sin(e.tickCount * 0.15F)));
    }

    @Override
    public ResourceLocation getTextureLocation(SporemawEntity entity) {
        return TEXTURE;
    }

    @Override
    public void render(SporemawEntity entity, float yaw, float partialTick, PoseStack poseStack, MultiBufferSource buffers,
                       int packedLight) {
        // A burrowed maw casts a smaller shadow.
        this.shadowRadius = entity.getState() == SporemawEntity.BURROWED ? 0.3F : 0.55F;
        super.render(entity, yaw, partialTick, poseStack, buffers, packedLight);
    }
}
