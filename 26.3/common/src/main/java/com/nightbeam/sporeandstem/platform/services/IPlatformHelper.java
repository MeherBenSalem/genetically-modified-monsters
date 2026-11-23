package com.nightbeam.sporeandstem.platform.services;

import net.minecraft.world.item.CreativeModeTab;

import java.nio.file.Path;

/** Loader-specific facts and builders the common code needs. */
public interface IPlatformHelper {

    /** "Fabric" or "NeoForge". */
    String getPlatformName();

    boolean isDevelopmentEnvironment();

    Path getConfigDirectory();

    /** A creative tab builder positioned the way the loader expects. */
    CreativeModeTab.Builder creativeTabBuilder();
}
