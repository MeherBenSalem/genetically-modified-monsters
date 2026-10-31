package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.entity.BloatshroomEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class BloatshroomRenderer extends MobRenderer<BloatshroomEntity, BloatshroomModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("bloatshroom"), "main");
    private static final ResourceLocation TEXTURE = SporeAndStem.id("textures/entity/bloatshroom/bloatshroom.png");

    public BloatshroomRenderer(EntityRendererProvider.Context context) {
        super(context, new BloatshroomModel(context.bakeLayer(LAYER)), 0.45F);
    }

    @Override
    public ResourceLocation getTextureLocation(BloatshroomEntity entity) {
        return TEXTURE;
    }

    /** Flashes white faster and faster as the fuse runs down, like a creeper. */
    @Override
    protected float getWhiteOverlayProgress(BloatshroomEntity entity, float partialTick) {
        float f = entity.getSwelling(partialTick);
        return (int) (f * 10.0F) % 2 == 0 ? 0.0F : Mth.clamp(f, 0.5F, 1.0F);
    }
}
