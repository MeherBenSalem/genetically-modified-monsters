package com.nightbeam.sporeandstem.client;

import com.nightbeam.sporeandstem.client.entity.BossRenderers;
import com.nightbeam.sporeandstem.client.entity.CreatureRenderers;

/** Creature renderers and model layers: the creatures in {@link CreatureRenderers}, the boss in {@link BossRenderers}. */
public final class ModEntityRenderers {

    private ModEntityRenderers() {
    }

    public static void register(ModClient.RendererSink sink) {
        CreatureRenderers.register(sink);
        BossRenderers.register(sink);
    }

    public static void registerLayers(ModClient.LayerSink sink) {
        CreatureRenderers.registerLayers(sink);
        BossRenderers.registerLayers(sink);
    }
}
