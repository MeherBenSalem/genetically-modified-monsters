package com.nightbeam.sporeandstem.client.entity.creature;

import com.mojang.blaze3d.vertex.PoseStack;
import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.SporelingEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

import java.util.EnumMap;
import java.util.Map;

public class SporelingRenderer extends MobRenderer<SporelingEntity, SporelingModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("sporeling"), "main");
    private static final Map<SporelingEntity.Variant, ResourceLocation> TEXTURES = new EnumMap<>(SporelingEntity.Variant.class);
    private static final ResourceLocation GLOW = SporeAndStem.id("textures/entity/sporeling/sporeling_glowcap_glow.png");

    static {
        for (SporelingEntity.Variant v : SporelingEntity.Variant.values()) {
            TEXTURES.put(v, SporeAndStem.id("textures/entity/sporeling/sporeling_" + v.id() + ".png"));
        }
    }

    public SporelingRenderer(EntityRendererProvider.Context context) {
        super(context, new SporelingModel(context.bakeLayer(LAYER)), 0.3F);
        this.addLayer(new GlowLayer<>(this, e -> GLOW, e -> e.getVariant() == SporelingEntity.Variant.GLOWCAP
                ? 0.8 + 0.2 * Mth.sin(e.tickCount * 0.08F) : 0.0));
    }

    @Override
    public ResourceLocation getTextureLocation(SporelingEntity entity) {
        return TEXTURES.get(entity.getVariant());
    }

    @Override
    protected void scale(SporelingEntity entity, PoseStack poseStack, float partialTick) {
        if (entity.isBaby()) {
            poseStack.scale(0.55F, 0.55F, 0.55F);
        }
    }
}
