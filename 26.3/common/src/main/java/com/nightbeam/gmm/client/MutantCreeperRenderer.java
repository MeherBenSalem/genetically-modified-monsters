package com.nightbeam.gmm.client;

import com.nightbeam.gmm.Gmm;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.monster.creeper.CreeperModel;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.state.CreeperRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.monster.Creeper;

public class MutantCreeperRenderer extends MobRenderer<Creeper, CreeperRenderState, CreeperModel> {
    private final Identifier texture;

    public MutantCreeperRenderer(EntityRendererProvider.Context context, String texturePath) {
        super(context, new CreeperModel(context.bakeLayer(ModelLayers.CREEPER)), 0.5F);
        this.texture = Identifier.fromNamespaceAndPath(Gmm.MOD_ID, "textures/entity/" + texturePath + ".png");
    }

    @Override
    public Identifier getTextureLocation(CreeperRenderState state) {
        return texture;
    }

    @Override
    public CreeperRenderState createRenderState() {
        return new CreeperRenderState();
    }

    @Override
    public void extractRenderState(Creeper entity, CreeperRenderState state, float partialTicks) {
        super.extractRenderState(entity, state, partialTicks);
        state.swelling = entity.getSwelling(partialTicks);
        state.isPowered = entity.isPowered();
    }
}
