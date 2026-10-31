package com.nightbeam.sporeandstem.platform.services;

import com.nightbeam.sporeandstem.registry.RegistryEntry;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;

import java.util.function.Supplier;

/**
 * Registers objects into vanilla registries. Fabric registers immediately; NeoForge defers to
 * {@code DeferredRegister}s, so callers must only resolve entries after registration has happened.
 */
public interface IRegistrar {

    <R, T extends R> RegistryEntry<T> register(ResourceKey<? extends Registry<R>> registry, String name, Supplier<T> factory);
}
