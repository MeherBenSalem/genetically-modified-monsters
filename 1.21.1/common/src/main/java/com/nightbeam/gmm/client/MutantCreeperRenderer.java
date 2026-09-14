package com.nightbeam.gmm.client;

import com.nightbeam.gmm.Gmm;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.client.model.CreeperModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.monster.Creeper;

public class MutantCreeperRenderer extends MobRenderer<Creeper, CreeperModel<Creeper>> {
    private final ResourceLocation texture;

    public MutantCreeperRenderer(EntityRendererProvider.Context context, String texturePath) {
        super(context, new CreeperModel<>(context.bakeLayer(ModelLayers.CREEPER)), 0.5F);
        this.texture = ResourceLocation.fromNamespaceAndPath(Gmm.MOD_ID, "textures/entity/" + texturePath + ".png");
    }

    @Override
    public ResourceLocation getTextureLocation(Creeper entity) {
        return texture;
    }
}
