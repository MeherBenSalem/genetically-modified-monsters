package com.nightbeam.sporeandstem.entity;

import com.nightbeam.sporeandstem.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

/** The Myceliarch (placeholder until the boss is implemented). */
public class MyceliarchEntity extends Monster {

    public MyceliarchEntity(EntityType<? extends MyceliarchEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 300.0);
    }

    /** Called by the Fruiting Heart. Returns false when it cannot be summoned here. */
    public static boolean summon(ServerLevel level, BlockPos pos, @Nullable Player summoner) {
        MyceliarchEntity boss = ModEntities.MYCELIARCH.get().create(level);
        if (boss == null) {
            return false;
        }
        boss.moveTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, level.random.nextFloat() * 360.0F, 0.0F);
        boss.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.TRIGGERED, null);
        return level.addFreshEntity(boss);
    }
}
