package com.nightbeam.sporeandstem.platform.services;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.nio.file.Path;
import java.util.function.Consumer;
import java.util.function.Supplier;

/** Loader-specific facts and builders the common code needs. */
public interface IPlatformHelper {

    /** "Fabric" or "NeoForge". */
    String getPlatformName();

    boolean isDevelopmentEnvironment();

    Path getConfigDirectory();

    /** Builds a creative tab the way the loader expects; fill gets one sink per refresh and passes it every item. */
    CreativeModeTab creativeTab(Component title, Supplier<ItemStack> icon, Consumer<Consumer<Item>> fill);
}
