#!/usr/bin/env python3
"""Generate GMM sources for 1.20.1 / 1.21.1 / 26.2 MultiLoader roots."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VARIANTS = [
    ("leap_creeper", "LeapCreeperEntity", "Leap Creeper", 0xAA0000, 0xFF4444, "LEAP"),
    ("climb_creeper", "ClimbCreeperEntity", "Climb Creeper", 0x880000, 0xCC2222, "CLIMB"),
    ("swift_creeper", "SwiftCreeperEntity", "Swift Creeper", 0xBB1100, 0xFF6633, "SWIFT"),
    ("adaptive_creeper", "AdaptiveCreeperEntity", "Adaptive Creeper", 0x990000, 0xDD5500, "ADAPTIVE"),
    ("overcharge_creeper", "OverchargeCreeperEntity", "Overcharge Creeper", 0xCC0000, 0xFFAA00, "OVERCHARGE"),
    ("silent_creeper", "SilentCreeperEntity", "Silent Creeper", 0x660000, 0x220000, "SILENT"),
    ("hunter_creeper", "HunterCreeperEntity", "Hunter Creeper", 0xAA0022, 0xFF0066, "HUNTER"),
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT)}")


def png_rgba(w: int, h: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            r, g, b, a = pixels[y * w + x]
            raw.extend((r, g, b, a))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(
        b"IDAT", zlib.compress(bytes(raw), 9)
    ) + chunk(b"IEND", b"")


def make_red_creeper_png(path: Path, seed: int = 0) -> None:
    """64x64 creeper-like red texture (skin layout approximation)."""
    w = h = 64
    pixels: list[tuple[int, int, int, int]] = []
    for y in range(h):
        for x in range(w):
            # Base deep red body
            r = 140 + ((x * 3 + y * 5 + seed) % 40)
            g = 10 + ((x + y + seed) % 20)
            b = 10 + ((x * 2 + seed) % 15)
            a = 255
            # Face region (approx head front UV) - darker eyes
            if 8 <= x < 16 and 8 <= y < 16:
                if (x in (10, 13) and 10 <= y <= 12) or (11 <= x <= 12 and y == 14):
                    r, g, b = 20, 0, 0
                else:
                    r, g, b = 190, 30, 30
            # Feet darker
            if y >= 32 and y < 48 and ((x % 16) < 8):
                r = max(80, r - 40)
            pixels.append((min(255, r), min(255, g), min(255, b), a))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_rgba(w, h, pixels))
    print(f"wrote texture {path.relative_to(ROOT)}")


def make_logo(path: Path) -> None:
    w = h = 128
    pixels = []
    for y in range(h):
        for x in range(w):
            # red circle on dark bg
            cx, cy = 64, 64
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 < 50 * 50:
                pixels.append((200, 20, 20, 255))
            elif d2 < 56 * 56:
                pixels.append((80, 0, 0, 255))
            else:
                pixels.append((20, 10, 10, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_rgba(w, h, pixels))


# ---------- shared Java templates ----------

COMMON_GMM = '''package com.nightbeam.gmm;

public final class Gmm {
    public static final String MOD_ID = "gmm";
    public static final String MOD_NAME = "Genetically Modified Monsters";

    private Gmm() {
    }
}
'''

MOD_ENTITIES = '''package com.nightbeam.gmm.registry;

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
'''

MOD_ITEMS = '''package com.nightbeam.gmm.registry;

import net.minecraft.world.item.Item;

import java.util.function.Supplier;

public final class ModItems {
    public static Supplier<Item> LEAP_CREEPER_SPAWN_EGG;
    public static Supplier<Item> CLIMB_CREEPER_SPAWN_EGG;
    public static Supplier<Item> SWIFT_CREEPER_SPAWN_EGG;
    public static Supplier<Item> ADAPTIVE_CREEPER_SPAWN_EGG;
    public static Supplier<Item> OVERCHARGE_CREEPER_SPAWN_EGG;
    public static Supplier<Item> SILENT_CREEPER_SPAWN_EGG;
    public static Supplier<Item> HUNTER_CREEPER_SPAWN_EGG;

    private ModItems() {
    }
}
'''


def mutant_base(version: str) -> str:
    # NBT API differs on 26.2
    if version == "26.2":
        save_methods = '''
    @Override
    protected void addAdditionalSaveData(net.minecraft.world.level.storage.ValueOutput output) {
        super.addAdditionalSaveData(output);
    }

    @Override
    protected void readAdditionalSaveData(net.minecraft.world.level.storage.ValueInput input) {
        super.readAdditionalSaveData(input);
    }
'''
    else:
        save_methods = '''
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
    }
'''
    nbt_import = "" if version == "26.2" else "import net.minecraft.nbt.CompoundTag;\n"

    jump_attr = ""
    if version != "1.20.1":
        # JUMP_STRENGTH exists 1.20.5+
        jump_attr = """
                .add(Attributes.JUMP_STRENGTH, 0.42D)"""

    return f'''package com.nightbeam.gmm.entity;

{nbt_import}import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

import java.lang.reflect.Field;

public abstract class MutantCreeperEntity extends Creeper {{
    protected MutantCreeperEntity(EntityType<? extends Creeper> type, Level level) {{
        super(type, level);
    }}

    public static AttributeSupplier.Builder createBaseAttributes() {{
        return Creeper.createAttributes()
                .add(Attributes.MAX_HEALTH, 24.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.28D)
                .add(Attributes.FOLLOW_RANGE, 24.0D){jump_attr};
    }}

    protected boolean isSilentMutant() {{
        return false;
    }}

    protected boolean canClimbWalls() {{
        return false;
    }}

    protected float explosionRadiusOverride() {{
        return -1.0F;
    }}

    @Override
    public boolean onClimbable() {{
        return (canClimbWalls() && this.horizontalCollision) || super.onClimbable();
    }}

    @Override
    protected SoundEvent getAmbientSound() {{
        return isSilentMutant() ? null : super.getAmbientSound();
    }}

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {{
        return isSilentMutant() ? null : super.getHurtSound(source);
    }}

    @Override
    protected SoundEvent getDeathSound() {{
        return isSilentMutant() ? SoundEvents.CREEPER_DEATH : super.getDeathSound();
    }}

    @Override
    public void playSound(SoundEvent sound, float volume, float pitch) {{
        if (isSilentMutant() && sound == SoundEvents.CREEPER_PRIMED) {{
            return;
        }}
        super.playSound(sound, volume, pitch);
    }}

    protected void applyExplosionRadiusOverride() {{
        float override = explosionRadiusOverride();
        if (override < 0.0F) {{
            return;
        }}
        try {{
            Field field = Creeper.class.getDeclaredField("explosionRadius");
            field.setAccessible(true);
            field.setInt(this, Math.round(override));
        }} catch (ReflectiveOperationException ignored) {{
            try {{
                for (Field field : Creeper.class.getDeclaredFields()) {{
                    if (field.getType() == int.class && !field.getName().contains("swell") && !field.getName().contains("Swell")) {{
                        field.setAccessible(true);
                        int current = field.getInt(this);
                        if (current == 3) {{
                            field.setInt(this, Math.round(override));
                            break;
                        }}
                    }}
                }}
            }} catch (ReflectiveOperationException ignored2) {{
            }}
        }}
    }}
{save_methods}}}
'''


def ai_goals(version: str) -> dict[str, str]:
    id_class = "Identifier" if version == "26.2" else "ResourceLocation"
    return {
        "LeapAttackGoal": '''package com.nightbeam.gmm.entity.ai;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Creeper;

import java.util.EnumSet;

public class LeapAttackGoal extends Goal {
    private final Creeper creeper;
    private final double leapStrength;
    private int cooldown;

    public LeapAttackGoal(Creeper creeper, double leapStrength) {
        this.creeper = creeper;
        this.leapStrength = leapStrength;
        this.setFlags(EnumSet.of(Flag.JUMP, Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (cooldown > 0) {
            cooldown--;
            return false;
        }
        LivingEntity target = creeper.getTarget();
        if (target == null || !creeper.onGround()) {
            return false;
        }
        double dist = creeper.distanceToSqr(target);
        return dist > 9.0D && dist < 100.0D && creeper.getRandom().nextInt(8) == 0;
    }

    @Override
    public void start() {
        LivingEntity target = creeper.getTarget();
        if (target == null) {
            return;
        }
        double dx = target.getX() - creeper.getX();
        double dz = target.getZ() - creeper.getZ();
        double len = Math.sqrt(dx * dx + dz * dz);
        if (len > 1.0E-4D) {
            creeper.setDeltaMovement(dx / len * 0.85D, leapStrength, dz / len * 0.85D);
        } else {
            creeper.setDeltaMovement(0.0D, leapStrength, 0.0D);
        }
        creeper.hasImpulse = true;
        cooldown = 40;
    }
}
''',
        "DodgeGoal": '''package com.nightbeam.gmm.entity.ai;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

public class DodgeGoal extends Goal {
    private final Creeper creeper;
    private int ticks;

    public DodgeGoal(Creeper creeper) {
        this.creeper = creeper;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        return creeper.getLastHurtByMob() != null && creeper.getLastHurtByMobTimestamp() + 20 > creeper.tickCount
                && creeper.getRandom().nextInt(3) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return ticks > 0;
    }

    @Override
    public void start() {
        ticks = 12;
        LivingEntity attacker = creeper.getLastHurtByMob();
        if (attacker == null) {
            return;
        }
        Vec3 away = creeper.position().subtract(attacker.position()).normalize().scale(0.7D);
        double side = creeper.getRandom().nextBoolean() ? 1.0D : -1.0D;
        Vec3 strafe = new Vec3(-away.z, 0.0D, away.x).scale(side * 0.55D);
        creeper.setDeltaMovement(creeper.getDeltaMovement().add(away.add(strafe).add(0.0D, 0.25D, 0.0D)));
        creeper.hasImpulse = true;
    }

    @Override
    public void tick() {
        ticks--;
    }
}
''',
        "HazardAvoidGoal": '''package com.nightbeam.gmm.entity.ai;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

public class HazardAvoidGoal extends Goal {
    private final Creeper creeper;
    private Vec3 flee;

    public HazardAvoidGoal(Creeper creeper) {
        this.creeper = creeper;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        BlockPos pos = creeper.blockPosition();
        for (BlockPos check : BlockPos.betweenClosed(pos.offset(-2, -1, -2), pos.offset(2, 1, 2))) {
            BlockState state = creeper.level().getBlockState(check);
            if (state.is(Blocks.LAVA) || state.is(Blocks.FIRE) || state.is(Blocks.SOUL_FIRE)
                    || state.is(Blocks.MAGMA_BLOCK) || state.is(Blocks.CACTUS) || state.is(BlockTags.CAMPFIRES)) {
                flee = creeper.position().subtract(Vec3.atCenterOf(check)).normalize().scale(1.1D);
                return true;
            }
        }
        return false;
    }

    @Override
    public void start() {
        if (flee != null) {
            creeper.getNavigation().stop();
            creeper.setDeltaMovement(creeper.getDeltaMovement().add(flee.x, 0.2D, flee.z));
            creeper.hasImpulse = true;
        }
    }

    @Override
    public boolean canContinueToUse() {
        return false;
    }
}
''',
        "PersistentTargetGoal": '''package com.nightbeam.gmm.entity.ai;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.target.TargetGoal;
import net.minecraft.world.entity.ai.targeting.TargetingConditions;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.player.Player;

import java.util.EnumSet;
import java.util.UUID;

public class PersistentTargetGoal extends TargetGoal {
    private final Creeper creeper;
    private final TargetingConditions conditions = TargetingConditions.forCombat().ignoreLineOfSight().range(64.0D);
    private UUID lockedId;
    private int recheck;

    public PersistentTargetGoal(Creeper creeper) {
        super(creeper, false, false);
        this.creeper = creeper;
        this.setFlags(EnumSet.of(Flag.TARGET));
    }

    @Override
    public boolean canUse() {
        LivingEntity current = creeper.getTarget();
        if (current instanceof Player player && player.isAlive() && !player.isCreative() && !player.isSpectator()) {
            lockedId = player.getUUID();
            return true;
        }
        if (lockedId != null) {
            Player player = creeper.level().getPlayerByUUID(lockedId);
            if (player != null && player.isAlive() && !player.isCreative() && !player.isSpectator()) {
                this.target = player;
                return true;
            }
        }
        Player nearest = creeper.level().getNearestPlayer(conditions, creeper);
        if (nearest != null) {
            lockedId = nearest.getUUID();
            this.target = nearest;
            return true;
        }
        return false;
    }

    @Override
    public void start() {
        creeper.setTarget(this.target);
        recheck = 0;
        super.start();
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity target = creeper.getTarget();
        if (target instanceof Player player && player.isAlive() && !player.isCreative() && !player.isSpectator()) {
            lockedId = player.getUUID();
            return true;
        }
        if (lockedId == null) {
            return false;
        }
        Player player = creeper.level().getPlayerByUUID(lockedId);
        if (player == null || !player.isAlive() || player.isCreative() || player.isSpectator()) {
            return false;
        }
        creeper.setTarget(player);
        return true;
    }

    @Override
    public void tick() {
        if (++recheck >= 10 && lockedId != null) {
            recheck = 0;
            Player player = creeper.level().getPlayerByUUID(lockedId);
            if (player != null) {
                creeper.setTarget(player);
                creeper.getNavigation().moveTo(player, 1.25D);
            }
        }
    }
}
''',
    }


def variant_sources(version: str) -> dict[str, str]:
    sources = {}
    sources["LeapCreeperEntity"] = '''package com.nightbeam.gmm.entity;

import com.nightbeam.gmm.entity.ai.LeapAttackGoal;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class LeapCreeperEntity extends MutantCreeperEntity {
    public LeapCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        AttributeSupplier.Builder builder = createBaseAttributes()
                .add(Attributes.MOVEMENT_SPEED, 0.27D)
                .add(Attributes.FOLLOW_RANGE, 28.0D);
        return builder;
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(1, new LeapAttackGoal(this, 1.15D));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (this.onGround() && this.getTarget() != null && this.random.nextInt(60) == 0) {
            this.setDeltaMovement(this.getDeltaMovement().add(0.0D, 0.55D, 0.0D));
            this.hasImpulse = true;
        }
    }
}
'''
    sources["ClimbCreeperEntity"] = '''package com.nightbeam.gmm.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class ClimbCreeperEntity extends MutantCreeperEntity {
    public ClimbCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes();
    }

    @Override
    protected boolean canClimbWalls() {
        return true;
    }

    @Override
    public void tick() {
        super.tick();
        if (this.horizontalCollision && canClimbWalls()) {
            this.setDeltaMovement(this.getDeltaMovement().x, 0.22D, this.getDeltaMovement().z);
        }
    }
}
'''
    sources["SwiftCreeperEntity"] = '''package com.nightbeam.gmm.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class SwiftCreeperEntity extends MutantCreeperEntity {
    public SwiftCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes()
                .add(Attributes.MOVEMENT_SPEED, 0.42D)
                .add(Attributes.FOLLOW_RANGE, 48.0D);
    }
}
'''
    sources["AdaptiveCreeperEntity"] = '''package com.nightbeam.gmm.entity;

import com.nightbeam.gmm.entity.ai.DodgeGoal;
import com.nightbeam.gmm.entity.ai.HazardAvoidGoal;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class AdaptiveCreeperEntity extends MutantCreeperEntity {
    public AdaptiveCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes()
                .add(Attributes.MOVEMENT_SPEED, 0.34D)
                .add(Attributes.FOLLOW_RANGE, 32.0D);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(1, new DodgeGoal(this));
        this.goalSelector.addGoal(1, new HazardAvoidGoal(this));
    }
}
'''
    sources["OverchargeCreeperEntity"] = '''package com.nightbeam.gmm.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class OverchargeCreeperEntity extends MutantCreeperEntity {
    public OverchargeCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
        this.applyExplosionRadiusOverride();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes();
    }

    @Override
    protected float explosionRadiusOverride() {
        // Vanilla charged uses radius 3 * 2 = 6; 2x charged => 12.
        return 12.0F;
    }

    @Override
    public void tick() {
        if (this.tickCount == 1) {
            this.applyExplosionRadiusOverride();
        }
        super.tick();
    }
}
'''
    sources["SilentCreeperEntity"] = '''package com.nightbeam.gmm.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

public class SilentCreeperEntity extends MutantCreeperEntity {
    public SilentCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes()
                .add(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED, 0.30D);
    }

    @Override
    protected boolean isSilentMutant() {
        return true;
    }
}
'''
    sources["HunterCreeperEntity"] = '''package com.nightbeam.gmm.entity;

import com.nightbeam.gmm.entity.ai.PersistentTargetGoal;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

public class HunterCreeperEntity extends MutantCreeperEntity {
    public HunterCreeperEntity(EntityType<? extends Creeper> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createBaseAttributes()
                .add(Attributes.MOVEMENT_SPEED, 0.33D)
                .add(Attributes.FOLLOW_RANGE, 64.0D);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.targetSelector.removeAllGoals(goal -> goal instanceof NearestAttackableTargetGoal);
        this.targetSelector.addGoal(1, new PersistentTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }
}
'''
    return sources


def renderer(version: str) -> str:
    res = "Identifier" if version == "26.2" else "ResourceLocation"
    res_import = (
        "import net.minecraft.resources.Identifier;"
        if version == "26.2"
        else "import net.minecraft.resources.ResourceLocation;"
    )
    if version == "1.20.1":
        loc = 'new ResourceLocation(Gmm.MOD_ID, "textures/entity/" + texturePath + ".png")'
    elif version == "26.2":
        loc = 'Identifier.fromNamespaceAndPath(Gmm.MOD_ID, "textures/entity/" + texturePath + ".png")'
    else:
        loc = 'ResourceLocation.fromNamespaceAndPath(Gmm.MOD_ID, "textures/entity/" + texturePath + ".png")'

    return f'''package com.nightbeam.gmm.client;

import com.nightbeam.gmm.Gmm;
import com.nightbeam.gmm.entity.MutantCreeperEntity;
{res_import}
import net.minecraft.client.model.CreeperModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.monster.Creeper;

public class MutantCreeperRenderer extends MobRenderer<Creeper, CreeperModel<Creeper>> {{
    private final {res} texture;

    public MutantCreeperRenderer(EntityRendererProvider.Context context, String texturePath) {{
        super(context, new CreeperModel<>(context.bakeLayer(ModelLayers.CREEPER)), 0.5F);
        this.texture = {loc};
    }}

    @Override
    public {res} getTextureLocation(Creeper entity) {{
        return texture;
    }}
}}
'''


def id_helper(version: str) -> str:
    if version == "1.20.1":
        return '''    private static ResourceLocation id(String path) {
        return new ResourceLocation(Gmm.MOD_ID, path);
    }'''
    if version == "26.2":
        return '''    private static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(Gmm.MOD_ID, path);
    }'''
    return '''    private static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(Gmm.MOD_ID, path);
    }'''


def fabric_main(version: str) -> str:
    res_import = (
        "import net.minecraft.resources.Identifier;"
        if version == "26.2"
        else "import net.minecraft.resources.ResourceLocation;"
    )
    res_type = "Identifier" if version == "26.2" else "ResourceLocation"

    egg_lines = []
    for vid, cls, name, c1, c2, const in VARIANTS:
        field = const + "_CREEPER"
        egg_field = const + "_CREEPER_SPAWN_EGG"
        if version == "26.2":
            egg_lines.append(
                f'        ModItems.{egg_field} = item("{vid}_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.{field}.get())));'
            )
        else:
            egg_lines.append(
                f'        ModItems.{egg_field} = item("{vid}_spawn_egg", () -> new SpawnEggItem(ModEntities.{field}.get(), {c1}, {c2}, new Item.Properties()));'
            )

    entity_regs = "\n".join(
        f'        ModEntities.{const}_CREEPER = entity("{vid}", EntityType.Builder.<{cls}>of({cls}::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    attr_regs = "\n".join(
        f'        FabricDefaultAttributeRegistry.register(ModEntities.{const}_CREEPER.get(), {cls}.createAttributes());'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    egg_accepts = "\n".join(
        f'            entries.accept(ModItems.{const}_CREEPER_SPAWN_EGG.get());'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    spawn_regs = "\n".join(
        f'        BiomeModifications.addSpawn(BiomeSelectors.foundInOverworld(), MobCategory.MONSTER, ModEntities.{const}_CREEPER.get(), 4, 1, 2);'
        for vid, cls, name, c1, c2, const in VARIANTS
    )

    egg_import = "" if version == "26.2" else "import net.minecraft.world.item.SpawnEggItem;\n"
    build_entity = (
        "builder.build(ResourceKey.create(Registries.ENTITY_TYPE, id(name)))"
        if version == "26.2"
        else "builder.build(name)"
    )
    extra_imports_26 = (
        "import net.minecraft.resources.ResourceKey;\nimport net.minecraft.core.registries.Registries;\n"
        if version == "26.2"
        else ""
    )

    entity_imports = "\n".join(f"import com.nightbeam.gmm.entity.{cls};" for _, cls, _, _, _, _ in VARIANTS)

    return f'''package com.nightbeam.gmm.fabric;

import com.nightbeam.gmm.Gmm;
{entity_imports}
import com.nightbeam.gmm.registry.ModEntities;
import com.nightbeam.gmm.registry.ModItems;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
{extra_imports_26}{res_import}
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
{egg_import}
import java.util.function.Supplier;

public class GmmFabric implements ModInitializer {{
    @Override
    public void onInitialize() {{
        registerContent();
{attr_regs}
{spawn_regs}
    }}

    private static void registerContent() {{
{entity_regs}
{chr(10).join(egg_lines)}
        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.SPAWN_EGGS).register(entries -> {{
{egg_accepts}
        }});
    }}

    private static <T extends Item> Supplier<T> item(String name, Supplier<T> factory) {{
        return register(name, () -> Registry.register(BuiltInRegistries.ITEM, id(name), factory.get()));
    }}

    private static <T extends net.minecraft.world.entity.Entity> Supplier<EntityType<T>> entity(String name, EntityType.Builder<T> builder) {{
        return register(name, () -> Registry.register(BuiltInRegistries.ENTITY_TYPE, id(name), {build_entity}));
    }}

    private static <T> Supplier<T> register(String name, Supplier<T> supplier) {{
        T value = supplier.get();
        return () -> value;
    }}

{id_helper(version)}
}}
'''


def fabric_client(version: str) -> str:
    regs = "\n".join(
        f'        EntityRendererRegistry.register(ModEntities.{const}_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "{vid}"));'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    return f'''package com.nightbeam.gmm.fabric.client;

import com.nightbeam.gmm.client.MutantCreeperRenderer;
import com.nightbeam.gmm.registry.ModEntities;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

public class GmmFabricClient implements ClientModInitializer {{
    @Override
    public void onInitializeClient() {{
{regs}
    }}
}}
'''


def forge_main_1201() -> str:
    entity_regs = "\n".join(
        f'''        RegistryObject<EntityType<{cls}>> {const.lower()} = ENTITIES.register("{vid}",
                () -> EntityType.Builder.<{cls}>of({cls}::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("{vid}"));
        ModEntities.{const}_CREEPER = {const.lower()};'''
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    egg_regs = "\n".join(
        f'        ModItems.{const}_CREEPER_SPAWN_EGG = ITEMS.register("{vid}_spawn_egg", () -> new SpawnEggItem(ModEntities.{const}_CREEPER.get(), {c1}, {c2}, new Item.Properties()));'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    attr_regs = "\n".join(
        f'        event.put(ModEntities.{const}_CREEPER.get(), {cls}.createAttributes().build());'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    egg_accepts = "\n".join(
        f'            event.accept(ModItems.{const}_CREEPER_SPAWN_EGG.get());'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    entity_imports = "\n".join(f"import com.nightbeam.gmm.entity.{cls};" for _, cls, _, _, _, _ in VARIANTS)
    return f'''package com.nightbeam.gmm.forge;

import com.nightbeam.gmm.Gmm;
{entity_imports}
import com.nightbeam.gmm.registry.ModEntities;
import com.nightbeam.gmm.registry.ModItems;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(Gmm.MOD_ID)
public class GmmForge {{
    private static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Gmm.MOD_ID);
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Gmm.MOD_ID);

    public GmmForge() {{
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        registerContent();
        ENTITIES.register(modBus);
        ITEMS.register(modBus);
        modBus.addListener(this::attributes);
        modBus.addListener(this::creativeTabs);
        MinecraftForge.EVENT_BUS.register(this);
    }}

    private static void registerContent() {{
{entity_regs}
{egg_regs}
    }}

    private void attributes(EntityAttributeCreationEvent event) {{
{attr_regs}
    }}

    private void creativeTabs(BuildCreativeModeTabContentsEvent event) {{
        if (event.getTabKey() == CreativeModeTabs.SPAWN_EGGS) {{
{egg_accepts}
        }}
    }}
}}
'''


def forge_client_1201() -> str:
    regs = "\n".join(
        f'        event.registerEntityRenderer(ModEntities.{const}_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "{vid}"));'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    return f'''package com.nightbeam.gmm.forge.client;

import com.nightbeam.gmm.Gmm;
import com.nightbeam.gmm.client.MutantCreeperRenderer;
import com.nightbeam.gmm.registry.ModEntities;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = Gmm.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class GmmForgeClient {{
    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {{
{regs}
    }}
}}
'''


def neoforge_main(version: str) -> str:
    if version == "26.2":
        entity_regs = "\n".join(
            f'''        DeferredHolder<EntityType<?>, EntityType<{cls}>> {const.lower()} = registerEntity("{vid}",
                EntityType.Builder.<{cls}>of({cls}::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8));
        ModEntities.{const}_CREEPER = {const.lower()};'''
            for vid, cls, name, c1, c2, const in VARIANTS
        )
        egg_regs = "\n".join(
            f'        ModItems.{const}_CREEPER_SPAWN_EGG = ITEMS.register("{vid}_spawn_egg", () -> new Item(new Item.Properties().spawnEgg(ModEntities.{const}_CREEPER.get())));'
            for vid, cls, name, c1, c2, const in VARIANTS
        )
        helper = '''
    private static <T extends net.minecraft.world.entity.Entity> DeferredHolder<EntityType<?>, EntityType<T>> registerEntity(String name, EntityType.Builder<T> builder) {
        ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, Identifier.fromNamespaceAndPath(Gmm.MOD_ID, name));
        return ENTITIES.register(name, () -> builder.build(key));
    }
'''
        extra_imports = """import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
"""
        egg_import = ""
    else:
        entity_regs = "\n".join(
            f'''        DeferredHolder<EntityType<?>, EntityType<{cls}>> {const.lower()} = ENTITIES.register("{vid}",
                () -> EntityType.Builder.<{cls}>of({cls}::new, MobCategory.MONSTER).sized(0.6F, 1.7F).clientTrackingRange(8).build("{vid}"));
        ModEntities.{const}_CREEPER = {const.lower()};'''
            for vid, cls, name, c1, c2, const in VARIANTS
        )
        egg_regs = "\n".join(
            f'        ModItems.{const}_CREEPER_SPAWN_EGG = ITEMS.register("{vid}_spawn_egg", () -> new SpawnEggItem(ModEntities.{const}_CREEPER.get(), {c1}, {c2}, new Item.Properties()));'
            for vid, cls, name, c1, c2, const in VARIANTS
        )
        helper = ""
        extra_imports = ""
        egg_import = "import net.minecraft.world.item.SpawnEggItem;\n"

    attr_regs = "\n".join(
        f'        event.put(ModEntities.{const}_CREEPER.get(), {cls}.createAttributes().build());'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    egg_accepts = "\n".join(
        f'            event.accept(ModItems.{const}_CREEPER_SPAWN_EGG.get());'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    entity_imports = "\n".join(f"import com.nightbeam.gmm.entity.{cls};" for _, cls, _, _, _, _ in VARIANTS)

    return f'''package com.nightbeam.gmm.neoforge;

import com.nightbeam.gmm.Gmm;
{entity_imports}
import com.nightbeam.gmm.registry.ModEntities;
import com.nightbeam.gmm.registry.ModItems;
import net.minecraft.core.registries.BuiltInRegistries;
{extra_imports}import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
{egg_import}import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

@Mod(Gmm.MOD_ID)
public class GmmNeoForge {{
    private static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(BuiltInRegistries.ENTITY_TYPE, Gmm.MOD_ID);
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(BuiltInRegistries.ITEM, Gmm.MOD_ID);

    public GmmNeoForge(IEventBus modBus) {{
        registerContent();
        ENTITIES.register(modBus);
        ITEMS.register(modBus);
        modBus.addListener(this::attributes);
        modBus.addListener(this::creativeTabs);
    }}

    private static void registerContent() {{
{entity_regs}
{egg_regs}
    }}

    private void attributes(EntityAttributeCreationEvent event) {{
{attr_regs}
    }}

    private void creativeTabs(BuildCreativeModeTabContentsEvent event) {{
        if (event.getTabKey() == CreativeModeTabs.SPAWN_EGGS) {{
{egg_accepts}
        }}
    }}
{helper}}}
'''


def neoforge_client(version: str) -> str:
    regs = "\n".join(
        f'        event.registerEntityRenderer(ModEntities.{const}_CREEPER.get(), ctx -> new MutantCreeperRenderer(ctx, "{vid}"));'
        for vid, cls, name, c1, c2, const in VARIANTS
    )
    bus = "net.neoforged.fml.common.EventBusSubscriber"
    return f'''package com.nightbeam.gmm.neoforge.client;

import com.nightbeam.gmm.Gmm;
import com.nightbeam.gmm.client.MutantCreeperRenderer;
import com.nightbeam.gmm.registry.ModEntities;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import {bus};
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

@EventBusSubscriber(modid = Gmm.MOD_ID, value = Dist.CLIENT)
public class GmmNeoForgeClient {{
    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {{
{regs}
    }}
}}
'''


def lang_json() -> str:
    lines = ['{']
    entries = []
    for vid, cls, name, c1, c2, const in VARIANTS:
        entries.append(f'  "entity.gmm.{vid}": "{name}"')
        entries.append(f'  "item.gmm.{vid}_spawn_egg": "{name} Spawn Egg"')
    entries.append('  "itemGroup.gmm": "Genetically Modified Monsters"')
    lines.append(",\n".join(entries))
    lines.append("}\n")
    return "\n".join(lines)


def spawn_egg_model(vid: str) -> str:
    return f'''{{
  "parent": "minecraft:item/template_spawn_egg"
}}
'''


def forge_biome_modifiers() -> list[tuple[str, str]]:
    out = []
    for vid, cls, name, c1, c2, const in VARIANTS:
        out.append(
            (
                f"fire_{vid}",  # unused
                f'''{{
  "type": "forge:add_spawns",
  "biomes": "#minecraft:is_overworld",
  "spawners": {{
    "type": "gmm:{vid}",
    "weight": 4,
    "minCount": 1,
    "maxCount": 2
  }}
}}
''',
            )
        )
        # fix name
        out[-1] = (vid, out[-1][1])
    return out


def neoforge_biome_modifiers() -> list[tuple[str, str]]:
    out = []
    for vid, *_ in VARIANTS:
        out.append(
            (
                vid,
                f'''{{
  "type": "neoforge:add_spawns",
  "biomes": "#minecraft:is_overworld",
  "spawners": {{
    "type": "gmm:{vid}",
    "weight": 4,
    "minCount": 1,
    "maxCount": 2
  }}
}}
''',
            )
        )
    return out


def generate_version(version: str) -> None:
    base = ROOT / version
    common_java = base / "common/src/main/java/com/nightbeam/gmm"
    common_res = base / "common/src/main/resources"

    write(common_java / "Gmm.java", COMMON_GMM)
    write(common_java / "registry/ModEntities.java", MOD_ENTITIES)
    write(common_java / "registry/ModItems.java", MOD_ITEMS)
    write(common_java / "entity/MutantCreeperEntity.java", mutant_base(version))
    for name, src in ai_goals(version).items():
        write(common_java / f"entity/ai/{name}.java", src)
    for name, src in variant_sources(version).items():
        write(common_java / f"entity/{name}.java", src)
    write(common_java / "client/MutantCreeperRenderer.java", renderer(version))

    write(common_res / "assets/gmm/lang/en_us.json", lang_json())
    for i, (vid, *_) in enumerate(VARIANTS):
        make_red_creeper_png(common_res / f"assets/gmm/textures/entity/{vid}.png", seed=i * 17)
        if version == "1.20.1":
            write(common_res / f"assets/gmm/models/item/{vid}_spawn_egg.json", spawn_egg_model(vid))

    make_logo(common_res / "logo.png")
    # also put logo where loaders expect
    make_logo(base / "fabric/src/main/resources/logo.png")
    if version == "1.20.1":
        make_logo(base / "forge/src/main/resources/logo.png")
    else:
        make_logo(base / "neoforge/src/main/resources/logo.png")

    # empty accesswidener optional
    write(common_res / "gmm.accesswidener", "accessWidener\tv1\tnamed\n")

    # Fabric
    write(base / "fabric/src/main/java/com/nightbeam/gmm/fabric/GmmFabric.java", fabric_main(version))
    write(base / "fabric/src/main/java/com/nightbeam/gmm/fabric/client/GmmFabricClient.java", fabric_client(version))

    if version == "1.20.1":
        write(base / "forge/src/main/java/com/nightbeam/gmm/forge/GmmForge.java", forge_main_1201())
        write(base / "forge/src/main/java/com/nightbeam/gmm/forge/client/GmmForgeClient.java", forge_client_1201())
        for vid, content in forge_biome_modifiers():
            write(common_res / f"data/gmm/forge/biome_modifier/{vid}_spawn.json", content)
    else:
        write(base / "neoforge/src/main/java/com/nightbeam/gmm/neoforge/GmmNeoForge.java", neoforge_main(version))
        write(
            base / "neoforge/src/main/java/com/nightbeam/gmm/neoforge/client/GmmNeoForgeClient.java",
            neoforge_client(version),
        )
        for vid, content in neoforge_biome_modifiers():
            write(common_res / f"data/gmm/neoforge/biome_modifier/{vid}_spawn.json", content)

    # Fix renderer unused import for 26.2
    if version == "26.2":
        p = common_java / "client/MutantCreeperRenderer.java"
        text = p.read_text(encoding="utf-8")
        text = text.replace("import net.minecraft.resources.ResourceLocation;\n", "")
        text = text.replace("import com.nightbeam.gmm.entity.MutantCreeperEntity;\n", "")
        p.write_text(text, encoding="utf-8")


def main() -> None:
    for version in ("1.20.1", "1.21.1", "26.2"):
        print(f"=== generating {version} ===")
        generate_version(version)

    # NOTICE + README
    write(
        ROOT / "NOTICE",
        """Genetically Modified Monsters
Copyright 2026 NightBeam Studio

This product is licensed under the Apache License, Version 2.0.
""",
    )
    write(
        ROOT / "README.md",
        """# Genetically Modified Monsters

NightBeam Studio MultiLoader mod: experimental red mutant Creepers with dangerous mutations.

## Supported versions

| Version root | Minecraft | Loaders | Java |
| --- | --- | --- | --- |
| `1.20.1/` | 1.20.1 | Fabric, Forge | 17 |
| `1.21.1/` | 1.21.1 | Fabric, NeoForge | 21 |
| `26.2/` | 26.2 | Fabric, NeoForge | 25 |

## Variants

| Entity | Ability |
| --- | --- |
| Leap Creeper | High-jump ambush leaps |
| Climb Creeper | Scales walls like a spider |
| Swift Creeper | Faster movement and long follow range |
| Adaptive Creeper | Dodges attacks and avoids hazards |
| Overcharge Creeper | Explosion up to 2× charged Creeper power |
| Silent Creeper | Silent until detonation |
| Hunter Creeper | Persistent target-lock on players |

## Building

```powershell
cd 1.21.1
.\\gradlew.bat build --no-daemon
```

Build all roots from the repository root (set `JAVA_HOME_17`, `JAVA_HOME_21`, `JAVA_HOME_25`):

```powershell
.\\gradlew.bat buildAll --no-daemon
```

## License

Apache License 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
""",
    )
    print("done")


if __name__ == "__main__":
    main()
