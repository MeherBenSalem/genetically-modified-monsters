package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.platform.Services;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;

public final class ModCreativeTabs {
    public static final RegistryEntry<CreativeModeTab> MAIN = Services.REGISTRAR.register(Registries.CREATIVE_MODE_TAB, "main",
            () -> Services.PLATFORM.creativeTabBuilder()
                    .title(Component.translatable("itemGroup.spore_and_stem"))
                    .icon(() -> new ItemStack(ModItems.GLOWCAP.get()))
                    .displayItems((parameters, output) -> ModItems.TAB.forEach(item -> output.accept(item.get())))
                    .build());

    private ModCreativeTabs() {
    }

    public static void init() {
    }
}
