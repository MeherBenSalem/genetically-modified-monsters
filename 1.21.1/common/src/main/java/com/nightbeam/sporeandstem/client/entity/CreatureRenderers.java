package com.nightbeam.sporeandstem.client.entity;

import com.nightbeam.sporeandstem.client.ModClient;
import com.nightbeam.sporeandstem.client.entity.creature.BloatshroomRenderer;
import com.nightbeam.sporeandstem.client.entity.creature.GlowmothRenderer;
import com.nightbeam.sporeandstem.client.entity.creature.MimicapRenderer;
import com.nightbeam.sporeandstem.client.entity.creature.ShamblerRenderer;
import com.nightbeam.sporeandstem.client.entity.creature.SporelingRenderer;
import com.nightbeam.sporeandstem.client.entity.creature.SporemawRenderer;
import com.nightbeam.sporeandstem.client.entity.creature.TrufflerRenderer;
import com.nightbeam.sporeandstem.client.entity.geo.BloatshroomGeometry;
import com.nightbeam.sporeandstem.client.entity.geo.GlowmothGeometry;
import com.nightbeam.sporeandstem.client.entity.geo.MimicapGeometry;
import com.nightbeam.sporeandstem.client.entity.geo.ShamblerGeometry;
import com.nightbeam.sporeandstem.client.entity.geo.SporelingGeometry;
import com.nightbeam.sporeandstem.client.entity.geo.SporemawGeometry;
import com.nightbeam.sporeandstem.client.entity.geo.TrufflerGeometry;
import com.nightbeam.sporeandstem.registry.ModEntities;

/** Renderers and model layers of the seven creatures (the Myceliarch has its own in BossRenderers). */
public final class CreatureRenderers {

    private CreatureRenderers() {
    }

    public static void register(ModClient.RendererSink sink) {
        sink.register(ModEntities.SPORELING.get(), SporelingRenderer::new);
        sink.register(ModEntities.BLOATSHROOM.get(), BloatshroomRenderer::new);
        sink.register(ModEntities.SHAMBLER.get(), ShamblerRenderer::new);
        sink.register(ModEntities.SPOREMAW.get(), SporemawRenderer::new);
        sink.register(ModEntities.MIMICAP.get(), MimicapRenderer::new);
        sink.register(ModEntities.GLOWMOTH.get(), GlowmothRenderer::new);
        sink.register(ModEntities.TRUFFLER.get(), TrufflerRenderer::new);
    }

    public static void registerLayers(ModClient.LayerSink sink) {
        sink.register(SporelingRenderer.LAYER, SporelingGeometry::createBodyLayer);
        sink.register(BloatshroomRenderer.LAYER, BloatshroomGeometry::createBodyLayer);
        sink.register(ShamblerRenderer.LAYER, ShamblerGeometry::createBodyLayer);
        sink.register(SporemawRenderer.LAYER, SporemawGeometry::createBodyLayer);
        sink.register(MimicapRenderer.LAYER, MimicapGeometry::createBodyLayer);
        sink.register(GlowmothRenderer.LAYER, GlowmothGeometry::createBodyLayer);
        sink.register(TrufflerRenderer.LAYER, TrufflerGeometry::createBodyLayer);
    }
}
