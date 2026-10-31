package com.nightbeam.sporeandstem.client.entity.creature;

import com.nightbeam.sporeandstem.client.entity.CreatureAnim;
import com.nightbeam.sporeandstem.client.entity.RigModel;
import com.nightbeam.sporeandstem.client.entity.anim.GlowmothAnimations;
import com.nightbeam.sporeandstem.entity.GlowmothEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class GlowmothModel extends RigModel<GlowmothEntity> {
    private final ModelPart body;

    public GlowmothModel(ModelPart root) {
        super(root);
        this.body = part("body");
    }

    @Override
    public void setupAnim(GlowmothEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw,
                          float headPitch) {
        resetPose();
        double dx = entity.getX() - entity.xo;
        double dz = entity.getZ() - entity.zo;
        double dy = entity.getY() - entity.yo;
        float speed = (float) Math.sqrt(dx * dx + dz * dz);
        float flying = Mth.clamp(speed * 12.0F, 0.0F, 1.0F);
        // Each moth is a little out of step with its neighbours.
        float age = ageInTicks + (entity.getId() % 7) * 3.0F;
        CreatureAnim.loop(this, GlowmothAnimations.FLY, age, 1.0F, flying);
        CreatureAnim.loop(this, GlowmothAnimations.HOVER, age, 1.0F, 1.0F - flying);
        body.xRot += Mth.clamp((float) dy * -8.0F, -0.5F, 0.5F);
    }
}
