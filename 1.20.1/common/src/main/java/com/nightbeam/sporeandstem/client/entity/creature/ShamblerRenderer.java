package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.ShamblerEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class ShamblerRenderer extends MobRenderer<ShamblerEntity, ShamblerModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("shambler"), "main");
    private static final ResourceLocation TEXTURE = SporeAndStem.id("textures/entity/shambler/shambler.png");
    private static final ResourceLocation GLOW = SporeAndStem.id("textures/entity/shambler/shambler_glow.png");

    public ShamblerRenderer(EntityRendererProvider.Context context) {
        super(context, new ShamblerModel(context.bakeLayer(LAYER)), 0.5F);
        this.addLayer(new GlowLayer<>(this, e -> GLOW, e -> 0.85 + 0.15 * Mth.sin(e.tickCount * 0.11F)));
    }

    @Override
    public ResourceLocation getTextureLocation(ShamblerEntity entity) {
        return TEXTURE;
    }
}
