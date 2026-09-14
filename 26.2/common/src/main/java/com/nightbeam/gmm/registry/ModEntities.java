package com.nightbeam.gmm.registry;

import com.nightbeam.gmm.entity.AdaptiveCreeperEntity;
import com.nightbeam.gmm.entity.ClimbCreeperEntity;
import com.nightbeam.gmm.entity.HunterCreeperEntity;
import com.nightbeam.gmm.entity.LeapCreeperEntity;
import com.nightbeam.gmm.entity.OverchargeCreeperEntity;
import com.nightbeam.gmm.entity.SilentCreeperEntity;
import com.nightbeam.gmm.entity.SwiftCreeperEntity;
import net.minecraft.world.entity.EntityType;

import java.util.function.Supplier;

public final class ModEntities {
    public static Supplier<EntityType<LeapCreeperEntity>> LEAP_CREEPER;
    public static Supplier<EntityType<ClimbCreeperEntity>> CLIMB_CREEPER;
    public static Supplier<EntityType<SwiftCreeperEntity>> SWIFT_CREEPER;
    public static Supplier<EntityType<AdaptiveCreeperEntity>> ADAPTIVE_CREEPER;
    public static Supplier<EntityType<OverchargeCreeperEntity>> OVERCHARGE_CREEPER;
    public static Supplier<EntityType<SilentCreeperEntity>> SILENT_CREEPER;
    public static Supplier<EntityType<HunterCreeperEntity>> HUNTER_CREEPER;

    private ModEntities() {
    }
}
