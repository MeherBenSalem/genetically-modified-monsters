package com.nightbeam.sporeandstem.gametest;

import com.nightbeam.sporeandstem.block.CultivationLogBlock;
import com.nightbeam.sporeandstem.block.FungusBlock;
import com.nightbeam.sporeandstem.block.ShelfFungusBlock;
import com.nightbeam.sporeandstem.block.VeilBulbs;
import com.nightbeam.sporeandstem.content.CultivationFungus;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModItems;
import com.nightbeam.sporeandstem.registry.RegistryEntry;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.phys.Vec3;

/**
 * In-world tests shared by both loaders (Fabric: {@code fabric-gametest} entrypoint, run with
 * {@code ./gradlew :fabric:runGametest}; NeoForge: {@code @GameTestHolder}, {@code ./gradlew :neoforge:runGameTestServer}).
 * The arena is {@code spore_and_stem:arena}: 13×18×13 of air on a stone floor. GameTest places it one block above
 * the helper's origin, so the floor is at relative y = 1 and the first air layer at y = 2.
 */
public final class SporeAndStemTests {
    public static final String TEMPLATE = "arena";

    private SporeAndStemTests() {
    }

    /** Every block has its item, its loot table loads, and every item and block is registered. */
    public static void contentIsComplete(GameTestHelper helper) {
        var registries = helper.getLevel().getServer().reloadableRegistries();
        for (RegistryEntry<? extends Block> entry : ModBlocks.WITH_ITEMS) {
            helper.assertTrue(entry.get().asItem() != Items.AIR, entry.id() + " has no item");
        }
        for (Block block : BuiltInRegistries.BLOCK) {
            if (!BuiltInRegistries.BLOCK.getKey(block).getNamespace().equals("spore_and_stem")) {
                continue;
            }
            ResourceKey<LootTable> key = block.getLootTable();
            if (key != null && !key.location().getPath().equals("empty")) {
                helper.assertTrue(registries.getLootTable(key) != LootTable.EMPTY, "missing loot table " + key.location());
            }
        }
        helper.succeed();
    }

    /**
     * Fungi live on fungus soil in any light, but not on bare stone in bright light. The light comes from glowstone, not
     * the sky: Forge's 1.20.1 GameTest world computes no sky light.
     */
    public static void fungiNeedFungusSoilInLight(GameTestHelper helper) {
        BlockPos soil = new BlockPos(2, 1, 2);
        helper.setBlock(soil, ModBlocks.MYCELIAL_SOIL.get());
        BlockPos lit = new BlockPos(6, 2, 6);
        helper.setBlock(lit.east(), Blocks.GLOWSTONE);
        BlockState morel = ModBlocks.MOREL.get().defaultBlockState();
        // Retried each tick until the light has spread.
        helper.succeedWhen(() -> {
            helper.assertTrue(morel.canSurvive(helper.getLevel(), helper.absolutePos(soil.above())), "morel should live on mycelial soil");
            BlockPos at = helper.absolutePos(lit);
            helper.assertFalse(morel.canSurvive(helper.getLevel(), at),
                    "morel should not live on brightly lit stone (light " + helper.getLevel().getRawBrightness(at, 0) + ")");
        });
    }

    /** A fungus inoculates a fresh Cultivation Log; a ripe log yields its fungus and falls back to the first flush. */
    public static void cultivationLogFruits(GameTestHelper helper) {
        BlockPos log = new BlockPos(3, 2, 3);
        helper.setBlock(log, ModBlocks.CULTIVATION_LOG.get());
        Player player = helper.makeMockPlayer(GameType.SURVIVAL);
        player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModItems.MOREL.get(), 2));
        helper.useBlock(log, player);
        helper.assertBlockProperty(log, CultivationLogBlock.FUNGUS, CultivationFungus.MOREL);
        helper.assertTrue(player.getMainHandItem().getCount() == 1, "inoculating should use one morel");
        helper.setBlock(log, helper.getBlockState(log).setValue(CultivationLogBlock.STAGE, 3));
        player.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
        helper.useBlock(log, player);
        helper.assertBlockProperty(log, CultivationLogBlock.STAGE, 1);
        helper.assertItemEntityPresent(ModItems.MOREL.get(), log, 2.0);
        helper.succeed();
    }

    /** Bouncecap caps cancel fall damage. */
    public static void bouncecapCapCancelsFallDamage(GameTestHelper helper) {
        BlockPos cap = new BlockPos(6, 1, 6);
        helper.setBlock(cap, ModBlocks.BOUNCECAP_CAP.get());
        Pig pig = helper.spawn(EntityType.PIG, new Vec3(6.5, 14.0, 6.5));
        helper.runAfterDelay(60, () -> {
            helper.assertTrue(pig.isAlive() && pig.getHealth() == pig.getMaxHealth(), "the pig should land unhurt");
            helper.succeed();
        });
    }

    /** Shelf fungus clings to a log and drops off when the log goes. */
    public static void shelfFungusNeedsItsTrunk(GameTestHelper helper) {
        BlockPos trunk = new BlockPos(2, 1, 2);
        BlockPos shelf = trunk.east();
        helper.setBlock(trunk, Blocks.OAK_LOG);
        BlockState state = ModBlocks.SHELF_FUNGUS.get().defaultBlockState().setValue(ShelfFungusBlock.FACING, Direction.EAST);
        helper.assertTrue(state.canSurvive(helper.getLevel(), helper.absolutePos(shelf)), "shelf fungus should cling to a log");
        helper.setBlock(shelf, state);
        helper.destroyBlock(trunk);
        helper.succeedWhenBlockPresent(Blocks.AIR, shelf);
    }

    /** Using a veil's glowing bulb picks Lumen Spores. */
    public static void veilBulbsGiveLumenSpores(GameTestHelper helper) {
        BlockPos veil = new BlockPos(3, 5, 3);
        helper.setBlock(veil.above(), Blocks.STONE);
        helper.setBlock(veil, ModBlocks.MYCELIAL_VEIL.get().defaultBlockState().setValue(VeilBulbs.BULB, true));
        helper.useBlock(veil, helper.makeMockPlayer(GameType.SURVIVAL));
        helper.assertBlockProperty(veil, VeilBulbs.BULB, false);
        helper.assertItemEntityPresent(ModItems.LUMEN_SPORES.get(), veil, 2.0);
        helper.succeed();
    }

    /** An axe strips fungal stems (Fabric registry / NeoForge tool event). */
    public static void axeStripsStems(GameTestHelper helper) {
        BlockPos stem = new BlockPos(2, 1, 2);
        helper.setBlock(stem, ModBlocks.GLOWCAP_WOOD.stem().get());
        Player player = helper.makeMockPlayer(GameType.SURVIVAL);
        player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(Items.IRON_AXE));
        helper.useBlock(stem, player);
        helper.assertBlockPresent(ModBlocks.GLOWCAP_WOOD.strippedStem().get(), stem);
        helper.assertBlockProperty(stem, RotatedPillarBlock.AXIS, Direction.Axis.Y);
        helper.succeed();
    }

    /** Mycosis wears you down but never kills; Spore Ward shrugs it off at once. */
    public static void mycosisNeverKillsAndWardBlocksIt(GameTestHelper helper) {
        Cow weak = helper.spawnWithNoFreeWill(EntityType.COW, new BlockPos(2, 2, 2));
        weak.setHealth(2.0F);
        weak.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 200, 3));
        Cow warded = helper.spawnWithNoFreeWill(EntityType.COW, new BlockPos(8, 2, 8));
        warded.addEffect(new MobEffectInstance(ModEffects.SPORE_WARD.holder(), 400));
        warded.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 200));
        helper.runAfterDelay(100, () -> {
            helper.assertTrue(weak.isAlive() && weak.getHealth() >= 1.0F, "Mycosis must never kill (alive=" + weak.isAlive()
                    + ", health=" + weak.getHealth() + ")");
            helper.assertFalse(warded.hasEffect(ModEffects.MYCOSIS.holder()), "Spore Ward should remove Mycosis");
            helper.succeed();
        });
    }

    /** A zombie that dies with Mycosis rises as a Shambler. */
    public static void infectedDeadRiseAsShamblers(GameTestHelper helper) {
        Zombie zombie = helper.spawnWithNoFreeWill(EntityType.ZOMBIE, new BlockPos(6, 2, 6));
        zombie.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 600));
        zombie.kill();
        helper.succeedWhen(() -> helper.assertEntityPresent(ModEntities.SHAMBLER.get()));
    }

    /** Forager's Stew cures Mycosis. */
    public static void foragersStewCuresMycosis(GameTestHelper helper) {
        Player player = helper.makeMockPlayer(GameType.SURVIVAL);
        player.addEffect(new MobEffectInstance(ModEffects.MYCOSIS.holder(), 600));
        ItemStack stew = new ItemStack(ModItems.FORAGERS_STEW.get());
        stew.getItem().finishUsingItem(stew, helper.getLevel(), player);
        helper.assertFalse(player.hasEffect(ModEffects.MYCOSIS.holder()), "Forager's Stew should cure Mycosis");
        helper.succeed();
    }

    /** A thrown Spore Bomb bursts into a lingering spore cloud. */
    public static void sporeBombBursts(GameTestHelper helper) {
        var bomb = helper.spawn(ModEntities.SPORE_BOMB.get(), new Vec3(6.5, 6.0, 6.5));
        bomb.setDeltaMovement(0.0, -0.5, 0.0);
        helper.succeedWhen(() -> helper.assertEntityPresent(EntityType.AREA_EFFECT_CLOUD));
    }

    /** Bone meal (the same feature as worldgen) grows a small Glowcap into a huge one. */
    public static void glowcapGrowsHuge(GameTestHelper helper) {
        BlockPos base = new BlockPos(6, 2, 6);
        helper.setBlock(base.below(), Blocks.DIRT);
        helper.setBlock(base, ModBlocks.GLOWCAP.get());
        BlockState state = helper.getBlockState(base);
        boolean grew = ((FungusBlock) state.getBlock()).growMushroom(helper.getLevel(), helper.absolutePos(base), state,
                helper.getLevel().getRandom());
        helper.assertTrue(grew, "the glowcap should grow");
        helper.assertBlockPresent(ModBlocks.GLOWCAP_WOOD.stem().get(), base);
        helper.succeed();
    }

    /** A Fruiting Heart used on mycelium calls up the Myceliarch. */
    public static void fruitingHeartSummonsTheMyceliarch(GameTestHelper helper) {
        BlockPos ground = new BlockPos(6, 1, 6);
        helper.setBlock(ground, Blocks.MYCELIUM);
        Player player = helper.makeMockPlayer(GameType.SURVIVAL);
        player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModItems.FRUITING_HEART.get()));
        helper.useBlock(ground, player);
        helper.succeedWhen(() -> helper.assertEntityPresent(ModEntities.MYCELIARCH.get()));
    }
}
