package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.MimicapEntity;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class MimicapRenderer extends MobRenderer<MimicapEntity, MimicapModel> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(SporeAndStem.id("mimicap"), "main");
    private static final ResourceLocation RED = SporeAndStem.id("textures/entity/mimicap/mimicap_red.png");
    private static final ResourceLocation BROWN = SporeAndStem.id("textures/entity/mimicap/mimicap_brown.png");
    private static final ResourceLocation GLOW = SporeAndStem.id("textures/entity/mimicap/mimicap_glow.png");

    public MimicapRenderer(EntityRendererProvider.Context context) {
        super(context, new MimicapModel(context.bakeLayer(LAYER)), 0.6F);
        // The eyes only light up once it is awake (and flicker as it wakes).
        this.addLayer(new GlowLayer<>(this, e -> GLOW, e -> switch (e.getPhase()) {
            case MimicapEntity.AWAKE -> 0.9 + 0.1 * Mth.sin(e.tickCount * 0.3F);
            case MimicapEntity.WAKING -> (e.tickCount / 2) % 2 == 0 ? 1.0 : 0.3;
            case MimicapEntity.SETTLING -> 0.3;
            default -> 0.0;
        }));
    }

    @Override
    public ResourceLocation getTextureLocation(MimicapEntity entity) {
        return entity.getVariant() == 0 ? RED : BROWN;
    }

    @Override
    protected float getFlipDegrees(MimicapEntity entity) {
        return 180.0F;
    }
}
