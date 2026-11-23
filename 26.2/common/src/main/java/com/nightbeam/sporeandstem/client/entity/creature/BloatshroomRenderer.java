package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderer;
import com.nightbeam.sporeandstem.entity.BloatshroomEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

public class BloatshroomRenderer extends CreatureRenderer<BloatshroomEntity, BloatshroomModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("bloatshroom"), "main");
    private static final Identifier TEXTURE = SporeAndStem.id("textures/entity/bloatshroom/bloatshroom.png");

    public BloatshroomRenderer(EntityRendererProvider.Context context) {
        super(context, new BloatshroomModel(context.bakeLayer(LAYER)), 0.45F);
    }

    @Override
    protected Identifier texture(BloatshroomEntity entity) {
        return TEXTURE;
    }

    /** Flashes white faster and faster as the fuse runs down, like a creeper. */
    protected float getWhiteOverlayProgress(CreatureRenderState<BloatshroomEntity> state) {
        if (state.entity == null) {
            return 0.0F;
        }
        float f = state.entity.getSwelling(state.partialTick);
        return (int) (f * 10.0F) % 2 == 0 ? 0.0F : Mth.clamp(f, 0.5F, 1.0F);
    }
}
