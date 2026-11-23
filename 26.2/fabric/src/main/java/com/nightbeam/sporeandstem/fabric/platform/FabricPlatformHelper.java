package com.nightbeam.sporeandstem.fabric.platform;

import com.nightbeam.sporeandstem.platform.services.IPlatformHelper;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.nio.file.Path;
import java.util.function.Consumer;
import java.util.function.Supplier;

public class FabricPlatformHelper implements IPlatformHelper {

    @Override
    public String getPlatformName() {
        return "Fabric";
    }

    @Override
    public boolean isDevelopmentEnvironment() {
        return FabricLoader.getInstance().isDevelopmentEnvironment();
    }

    @Override
    public Path getConfigDirectory() {
        return FabricLoader.getInstance().getConfigDir();
    }

    @Override
    public CreativeModeTab creativeTab(Component title, Supplier<ItemStack> icon, Consumer<Consumer<Item>> fill) {
        return FabricCreativeModeTab.builder().title(title).icon(icon).displayItems((parameters, output) -> fill.accept(output::accept)).build();
    }
}
