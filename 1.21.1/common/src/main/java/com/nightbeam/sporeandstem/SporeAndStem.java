package com.nightbeam.sporeandstem;

import com.nightbeam.sporeandstem.config.SporeConfig;
import com.nightbeam.sporeandstem.registry.ModArmorMaterials;
import com.nightbeam.sporeandstem.registry.ModBlocks;
import com.nightbeam.sporeandstem.registry.ModCreativeTabs;
import com.nightbeam.sporeandstem.registry.ModEffects;
import com.nightbeam.sporeandstem.registry.ModEntities;
import com.nightbeam.sporeandstem.registry.ModFeatures;
import com.nightbeam.sporeandstem.registry.ModItems;
import com.nightbeam.sporeandstem.registry.ModParticles;
import com.nightbeam.sporeandstem.registry.ModSounds;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Spore &amp; Stem: a whole kingdom of fungi. Loader entry points call {@link #init()} first. */
public final class SporeAndStem {
    public static final String MOD_ID = "spore_and_stem";
    public static final String MOD_NAME = "Spore & Stem";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_NAME);

    private SporeAndStem() {
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }

    /** Registers everything, in vanilla registry order so NeoForge's deferred registers resolve cleanly. */
    public static void init() {
        SporeConfig.load();
        ModSounds.init();
        ModEffects.init();
        ModBlocks.init();
        ModEntities.init();
        ModArmorMaterials.init();
        ModItems.init();
        ModParticles.init();
        ModFeatures.init();
        ModCreativeTabs.init();
        LOGGER.info("{} is growing", MOD_NAME);
    }
}
