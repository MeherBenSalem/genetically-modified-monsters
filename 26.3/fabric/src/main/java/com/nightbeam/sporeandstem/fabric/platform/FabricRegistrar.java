package com.nightbeam.sporeandstem.fabric.platform;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.platform.services.IRegistrar;
import com.nightbeam.sporeandstem.registry.RegistryEntry;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.Identifier;

import java.util.function.Supplier;

/** Fabric registers straight away, in call order. */
public class FabricRegistrar implements IRegistrar {

    @Override
    @SuppressWarnings("unchecked")
    public <R, T extends R> RegistryEntry<T> register(ResourceKey<? extends Registry<R>> registryKey, String name, Supplier<T> factory) {
        Registry<R> registry = (Registry<R>) BuiltInRegistries.REGISTRY.getValue(registryKey.identifier());
        if (registry == null) {
            throw new IllegalStateException("Unknown registry " + registryKey.identifier());
        }
        Identifier id = SporeAndStem.id(name);
        T value = factory.get();
        Holder<R> holder = Registry.registerForHolder(registry, id, value);
        return new Entry<>(id, value, (Holder<T>) holder);
    }

    private record Entry<T>(Identifier id, T value, Holder<T> holder) implements RegistryEntry<T> {
        @Override
        public T get() {
            return value;
        }
    }
}
