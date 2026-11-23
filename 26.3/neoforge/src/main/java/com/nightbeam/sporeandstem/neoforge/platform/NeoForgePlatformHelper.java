package com.nightbeam.sporeandstem.neoforge.platform;

import com.nightbeam.sporeandstem.platform.services.IPlatformHelper;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.fml.loading.FMLPaths;

import java.nio.file.Path;
import java.util.function.Consumer;
import java.util.function.Supplier;

public class NeoForgePlatformHelper implements IPlatformHelper {

    @Override
    public String getPlatformName() {
        return "NeoForge";
    }

    @Override
    public boolean isDevelopmentEnvironment() {
        return !FMLEnvironment.isProduction();
    }

    @Override
    public Path getConfigDirectory() {
        return FMLPaths.CONFIGDIR.get();
    }

    @Override
    public CreativeModeTab creativeTab(Component title, Supplier<ItemStack> icon, Consumer<Consumer<Item>> fill) {
        return CreativeModeTab.builder().title(title).icon(icon).displayItems((parameters, output) -> fill.accept(output::accept)).build();
    }
}
