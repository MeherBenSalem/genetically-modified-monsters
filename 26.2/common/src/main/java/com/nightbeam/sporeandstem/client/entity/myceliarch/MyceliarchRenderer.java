package com.nightbeam.sporeandstem.client.entity.myceliarch;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderState;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderer;
import com.nightbeam.sporeandstem.client.entity.GlowLayer;
import com.nightbeam.sporeandstem.entity.MyceliarchEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * Draws the Myceliarch with its emissive gills, veins and eyes: a slow pulse in the first bloom, full and with more
 * veins in the second, fading as it dies. It does not topple over on death (its own collapse animation plays) and
 * casts no shadow while it is still underground.
 */
public class MyceliarchRenderer extends CreatureRenderer<MyceliarchEntity, MyceliarchModel> {
    private static final Identifier TEXTURE = SporeAndStem.id("textures/entity/myceliarch/myceliarch.png");
    private static final Identifier GLOW = SporeAndStem.id("textures/entity/myceliarch/myceliarch_glow.png");
    private static final Identifier BLOOM_GLOW = SporeAndStem.id("textures/entity/myceliarch/myceliarch_bloom_glow.png");
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
    protected Identifier texture(MyceliarchEntity entity) {
        return TEXTURE;
    }

    /** No shadow while it is still underground or sinking back into the ground. */
    public float getShadowRadius(CreatureRenderState<MyceliarchEntity> state) {
        MyceliarchEntity entity = state.entity;
        if (entity == null) {
            return SHADOW;
        }
        float underground = 0.0F;
        if (entity.isEmerging() && entity.emergeState.isStarted()) {
            float t = entity.emergeState.getTimeInMillis(state.ageInTicks) / 1000.0F;
            underground = t < 3.4F ? 1.0F : Math.max(0.0F, 1.0F - (t - 3.4F) / 1.2F);
        }
        int collapse = entity.getCollapseTicks();
        float sinking = collapse > 30 ? Math.min(1.0F, (collapse - 30) / 25.0F) : 0.0F;
        return SHADOW * (1.0F - Math.max(underground, sinking));
    }

    /** It does not topple over on death: its own collapse animation plays. */
    public float getFlipDegrees() {
        return 0.0F;
    }
}
