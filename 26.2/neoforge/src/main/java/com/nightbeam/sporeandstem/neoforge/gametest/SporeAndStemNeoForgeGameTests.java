package com.nightbeam.sporeandstem.neoforge.gametest;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.gametest.SporeAndStemTests;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.FunctionGameTestInstance;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.gametest.framework.TestData;
import net.minecraft.gametest.framework.TestEnvironmentDefinition;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.RegisterGameTestsEvent;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.function.Consumer;

/**
 * Registers the shared {@link SporeAndStemTests} with NeoForge: one test function per test, and one test instance per
 * function in template {@code spore_and_stem:arena}. Runs with {@code ./gradlew :neoforge:runGameTestServer}.
 */
public final class SporeAndStemNeoForgeGameTests {
    private static final DeferredRegister<Consumer<GameTestHelper>> FUNCTIONS = DeferredRegister.create(Registries.TEST_FUNCTION,
            SporeAndStem.MOD_ID);

    private record TestEntry(String name, int maxTicks, Consumer<GameTestHelper> function) {
    }

    private static final TestEntry[] TESTS = {
            new TestEntry("content_is_complete", 100, SporeAndStemTests::contentIsComplete),
            new TestEntry("fungi_need_fungus_soil_in_light", 100, SporeAndStemTests::fungiNeedFungusSoilInLight),
            new TestEntry("cultivation_log_fruits", 100, SporeAndStemTests::cultivationLogFruits),
            new TestEntry("bouncecap_cap_cancels_fall_damage", 200, SporeAndStemTests::bouncecapCapCancelsFallDamage),
            new TestEntry("shelf_fungus_needs_its_trunk", 100, SporeAndStemTests::shelfFungusNeedsItsTrunk),
            new TestEntry("veil_bulbs_give_lumen_spores", 100, SporeAndStemTests::veilBulbsGiveLumenSpores),
            new TestEntry("axe_strips_stems", 100, SporeAndStemTests::axeStripsStems),
            new TestEntry("mycosis_never_kills_and_ward_blocks_it", 200, SporeAndStemTests::mycosisNeverKillsAndWardBlocksIt),
            new TestEntry("infected_dead_rise_as_shamblers", 200, SporeAndStemTests::infectedDeadRiseAsShamblers),
            new TestEntry("foragers_stew_cures_mycosis", 100, SporeAndStemTests::foragersStewCuresMycosis),
            new TestEntry("spore_bomb_bursts", 100, SporeAndStemTests::sporeBombBursts),
            new TestEntry("glowcap_grows_huge", 100, SporeAndStemTests::glowcapGrowsHuge),
            new TestEntry("fruiting_heart_summons_the_myceliarch", 100, SporeAndStemTests::fruitingHeartSummonsTheMyceliarch),
    };

    static {
        for (TestEntry test : TESTS) {
            FUNCTIONS.register(test.name(), () -> test.function());
        }
    }

    private SporeAndStemNeoForgeGameTests() {
    }

    public static void register(IEventBus modBus) {
        FUNCTIONS.register(modBus);
        modBus.addListener(SporeAndStemNeoForgeGameTests::registerInstances);
    }

    private static void registerInstances(RegisterGameTestsEvent event) {
        Holder<TestEnvironmentDefinition<?>> environment = event.registerEnvironment(SporeAndStem.id("default"),
                new TestEnvironmentDefinition.AllOf());
        Identifier template = SporeAndStem.id(SporeAndStemTests.TEMPLATE);
        for (TestEntry test : TESTS) {
            Identifier id = SporeAndStem.id(test.name());
            event.registerTest(id, new FunctionGameTestInstance(ResourceKey.create(Registries.TEST_FUNCTION, id),
                    new TestData<>(environment, template, test.maxTicks(), 0, true)));
        }
    }
}
