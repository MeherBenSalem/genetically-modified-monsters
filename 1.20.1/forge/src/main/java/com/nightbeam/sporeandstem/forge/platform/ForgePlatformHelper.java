package com.nightbeam.sporeandstem.forge.platform;

import com.nightbeam.sporeandstem.platform.services.IPlatformHelper;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.fml.loading.FMLLoader;
import net.minecraftforge.fml.loading.FMLPaths;

import java.nio.file.Path;
import java.util.function.Supplier;

public class ForgePlatformHelper implements IPlatformHelper {

    @Override
    public String getPlatformName() {
        return "Forge";
    }

    @Override
    public boolean isDevelopmentEnvironment() {
        return !FMLLoader.isProduction();
    }

    @Override
    public Path getConfigDirectory() {
        return FMLPaths.CONFIGDIR.get();
    }

    @Override
    public CreativeModeTab.Builder creativeTabBuilder() {
        return CreativeModeTab.builder();
    }

    @Override
    public Item spawnEgg(Supplier<? extends EntityType<? extends Mob>> type, int base, int spots, Item.Properties properties) {
        return new ForgeSpawnEggItem(type, base, spots, properties);
    }

    @Override
    public FoodProperties.Builder modEffect(FoodProperties.Builder builder, Supplier<MobEffectInstance> effect, float chance) {
        return builder.effect(effect, chance);
    }
}
