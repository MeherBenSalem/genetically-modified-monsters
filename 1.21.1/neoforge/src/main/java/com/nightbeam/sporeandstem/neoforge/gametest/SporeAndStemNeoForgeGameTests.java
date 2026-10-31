package com.nightbeam.sporeandstem.neoforge.gametest;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.gametest.SporeAndStemTests;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Runs with {@code ./gradlew :neoforge:runGameTestServer}. */
@GameTestHolder(SporeAndStem.MOD_ID)
@PrefixGameTestTemplate(false)
public class SporeAndStemNeoForgeGameTests {

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void contentIsComplete(GameTestHelper helper) {
        SporeAndStemTests.contentIsComplete(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void fungiNeedFungusSoilInLight(GameTestHelper helper) {
        SporeAndStemTests.fungiNeedFungusSoilInLight(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void cultivationLogFruits(GameTestHelper helper) {
        SporeAndStemTests.cultivationLogFruits(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 200)
    public static void bouncecapCapCancelsFallDamage(GameTestHelper helper) {
        SporeAndStemTests.bouncecapCapCancelsFallDamage(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void shelfFungusNeedsItsTrunk(GameTestHelper helper) {
        SporeAndStemTests.shelfFungusNeedsItsTrunk(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void veilBulbsGiveLumenSpores(GameTestHelper helper) {
        SporeAndStemTests.veilBulbsGiveLumenSpores(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void axeStripsStems(GameTestHelper helper) {
        SporeAndStemTests.axeStripsStems(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 200)
    public static void mycosisNeverKillsAndWardBlocksIt(GameTestHelper helper) {
        SporeAndStemTests.mycosisNeverKillsAndWardBlocksIt(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 200)
    public static void infectedDeadRiseAsShamblers(GameTestHelper helper) {
        SporeAndStemTests.infectedDeadRiseAsShamblers(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void foragersStewCuresMycosis(GameTestHelper helper) {
        SporeAndStemTests.foragersStewCuresMycosis(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void sporeBombBursts(GameTestHelper helper) {
        SporeAndStemTests.sporeBombBursts(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void glowcapGrowsHuge(GameTestHelper helper) {
        SporeAndStemTests.glowcapGrowsHuge(helper);
    }

    @GameTest(template = SporeAndStemTests.TEMPLATE, timeoutTicks = 100)
    public static void fruitingHeartSummonsTheMyceliarch(GameTestHelper helper) {
        SporeAndStemTests.fruitingHeartSummonsTheMyceliarch(helper);
    }
}
