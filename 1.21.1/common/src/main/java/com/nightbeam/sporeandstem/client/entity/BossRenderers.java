package com.nightbeam.sporeandstem.client.entity;

import com.nightbeam.sporeandstem.client.ModClient;
import com.nightbeam.sporeandstem.client.entity.geo.MyceliarchGeometry;
import com.nightbeam.sporeandstem.client.entity.geo.RootSpikeGeometry;
import com.nightbeam.sporeandstem.client.entity.myceliarch.MyceliarchModel;
import com.nightbeam.sporeandstem.client.entity.myceliarch.MyceliarchRenderer;
import com.nightbeam.sporeandstem.client.entity.rootspike.RootSpikeModel;
import com.nightbeam.sporeandstem.client.entity.rootspike.RootSpikeRenderer;
import com.nightbeam.sporeandstem.registry.ModEntities;

/** The Myceliarch and its Root Spikes. */
public final class BossRenderers {

    private BossRenderers() {
    }

    public static void register(ModClient.RendererSink sink) {
        sink.register(ModEntities.MYCELIARCH.get(), MyceliarchRenderer::new);
        sink.register(ModEntities.ROOT_SPIKE.get(), RootSpikeRenderer::new);
    }

    public static void registerLayers(ModClient.LayerSink sink) {
        sink.register(MyceliarchModel.LAYER, MyceliarchGeometry::createBodyLayer);
        sink.register(RootSpikeModel.LAYER, RootSpikeGeometry::createBodyLayer);
    }
}
