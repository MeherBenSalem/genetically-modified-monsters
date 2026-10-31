package com.nightbeam.sporeandstem.fabric.gametest;

import com.nightbeam.sporeandstem.gametest.SporeAndStemTests;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;

/** Runs with {@code ./gradlew :fabric:runGametest}. */
public class SporeAndStemFabricGameTests {
    private static final String TEMPLATE = "spore_and_stem:" + SporeAndStemTests.TEMPLATE;

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void contentIsComplete(GameTestHelper helper) {
        SporeAndStemTests.contentIsComplete(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void fungiNeedFungusSoilInLight(GameTestHelper helper) {
        SporeAndStemTests.fungiNeedFungusSoilInLight(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void cultivationLogFruits(GameTestHelper helper) {
        SporeAndStemTests.cultivationLogFruits(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 200)
    public void bouncecapCapCancelsFallDamage(GameTestHelper helper) {
        SporeAndStemTests.bouncecapCapCancelsFallDamage(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void shelfFungusNeedsItsTrunk(GameTestHelper helper) {
        SporeAndStemTests.shelfFungusNeedsItsTrunk(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void veilBulbsGiveLumenSpores(GameTestHelper helper) {
        SporeAndStemTests.veilBulbsGiveLumenSpores(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void axeStripsStems(GameTestHelper helper) {
        SporeAndStemTests.axeStripsStems(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 200)
    public void mycosisNeverKillsAndWardBlocksIt(GameTestHelper helper) {
        SporeAndStemTests.mycosisNeverKillsAndWardBlocksIt(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 200)
    public void infectedDeadRiseAsShamblers(GameTestHelper helper) {
        SporeAndStemTests.infectedDeadRiseAsShamblers(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void foragersStewCuresMycosis(GameTestHelper helper) {
        SporeAndStemTests.foragersStewCuresMycosis(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void sporeBombBursts(GameTestHelper helper) {
        SporeAndStemTests.sporeBombBursts(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void glowcapGrowsHuge(GameTestHelper helper) {
        SporeAndStemTests.glowcapGrowsHuge(helper);
    }

    @GameTest(template = TEMPLATE, timeoutTicks = 100)
    public void fruitingHeartSummonsTheMyceliarch(GameTestHelper helper) {
        SporeAndStemTests.fruitingHeartSummonsTheMyceliarch(helper);
    }
}
