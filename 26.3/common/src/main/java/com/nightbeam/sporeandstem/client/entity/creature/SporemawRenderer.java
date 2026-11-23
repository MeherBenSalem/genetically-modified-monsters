package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderer;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.SporemawEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

public class SporemawRenderer extends CreatureRenderer<SporemawEntity, SporemawModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("sporemaw"), "main");
    private static final Identifier TEXTURE = SporeAndStem.id("textures/entity/sporemaw/sporemaw.png");
    private static final Identifier GLOW = SporeAndStem.id("textures/entity/sporemaw/sporemaw_glow.png");

    public SporemawRenderer(EntityRendererProvider.Context context) {
        super(context, new SporemawModel(context.bakeLayer(LAYER)), 0.55F);
        this.addLayer(new GlowLayer<>(this, e -> GLOW, e -> e.getState() == SporemawEntity.BURROWED ? 0.35
                : 0.8 + 0.2 * Mth.sin(e.tickCount * 0.15F)));
    }

    @Override
    protected Identifier texture(SporemawEntity entity) {
        return TEXTURE;
    }

    /** A smaller shadow while it hides in the ground. */
    public float getShadowRadius(CreatureRenderState<SporemawEntity> state) {
        return state.entity != null && state.entity.getState() == SporemawEntity.BURROWED ? 0.3F : 0.55F;
    }
}
