package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.GlowmothEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class GlowmothRenderer extends MobRenderer<GlowmothEntity, GlowmothModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("glowmoth"), "main");
    private static final ResourceLocation TEXTURE = SporeAndStem.id("textures/entity/glowmoth/glowmoth.png");
    private static final ResourceLocation GLOW = SporeAndStem.id("textures/entity/glowmoth/glowmoth_glow.png");

    public GlowmothRenderer(EntityRendererProvider.Context context) {
        super(context, new GlowmothModel(context.bakeLayer(LAYER)), 0.15F);
        this.addLayer(new GlowLayer<>(this, e -> GLOW, e -> 0.75 + 0.25 * Mth.sin((e.tickCount + e.getId() * 13) * 0.12F)));
    }

    @Override
    public ResourceLocation getTextureLocation(GlowmothEntity entity) {
        return TEXTURE;
    }

    /** Moths glow faintly themselves. */
    @Override
    protected int getBlockLightLevel(GlowmothEntity entity, BlockPos pos) {
        return Math.max(9, super.getBlockLightLevel(entity, pos));
    }
}
