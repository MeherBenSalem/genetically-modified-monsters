package com.nightbeam.sporeandstem.client.entity;

import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

/**
 * Base for the generated-geometry creature models: holds the "root" part, resets the pose every frame (so keyframed
 * animations always start from the rest pose) and turns a head toward where the creature looks.
 */
public abstract class RigModel<T extends Entity> extends HierarchicalModel<T> {
    private final ModelPart root;

    protected RigModel(ModelPart root) {
        this.root = root.getChild("root");
    }

    @Override
    public ModelPart root() {
        return root;
    }

    protected ModelPart part(String name) {
        return this.root().getAllParts().filter(p -> p.hasChild(name)).findFirst()
                .map(p -> p.getChild(name))
                .orElseThrow(() -> new IllegalArgumentException("No model part " + name));
    }

    protected void resetPose() {
        this.root().getAllParts().forEach(ModelPart::resetPose);
    }

    /** Adds the look rotation (degrees from the renderer) to a head part, clamped. */
    protected static void look(ModelPart head, float netHeadYaw, float headPitch, float maxYaw, float maxPitch) {
        head.yRot += Mth.clamp(netHeadYaw, -maxYaw, maxYaw) * Mth.DEG_TO_RAD;
        head.xRot += Mth.clamp(headPitch, -maxPitch, maxPitch) * Mth.DEG_TO_RAD;
    }
}
