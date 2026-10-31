package com.nightbeam.sporeandstem.fabric.platform;

import com.nightbeam.sporeandstem.platform.services.IPlatformHelper;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;

import java.nio.file.Path;
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
    public CreativeModeTab.Builder creativeTabBuilder() {
        return FabricItemGroup.builder();
    }

    @Override
    public Item spawnEgg(Supplier<? extends EntityType<? extends Mob>> type, int base, int spots, Item.Properties properties) {
        return new SpawnEggItem(type.get(), base, spots, properties);
    }

    @Override
    public FoodProperties.Builder modEffect(FoodProperties.Builder builder, Supplier<MobEffectInstance> effect, float chance) {
        return builder.effect(effect.get(), chance);
    }
}
