package com.nightbeam.sporeandstem.neoforge.platform;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.platform.services.IRegistrar;
import com.nightbeam.sporeandstem.registry.RegistryEntry;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

/** One {@link DeferredRegister} per vanilla registry; {@link #registerAll} hooks them onto the mod bus. */
public class NeoForgeRegistrar implements IRegistrar {
    private static final Map<ResourceKey<?>, DeferredRegister<?>> REGISTERS = new LinkedHashMap<>();

    @Override
    @SuppressWarnings("unchecked")
    public <R, T extends R> RegistryEntry<T> register(ResourceKey<? extends Registry<R>> registryKey, String name, Supplier<T> factory) {
        DeferredRegister<R> register = (DeferredRegister<R>) REGISTERS.computeIfAbsent(registryKey,
                key -> DeferredRegister.create(registryKey, SporeAndStem.MOD_ID));
        return new Entry<>(register.register(name, factory));
    }

    public static void registerAll(IEventBus modBus) {
        REGISTERS.values().forEach(register -> register.register(modBus));
    }

    private record Entry<R, T extends R>(DeferredHolder<R, T> deferred) implements RegistryEntry<T> {
        @Override
        public T get() {
            return deferred.get();
        }

        @Override
        public ResourceLocation id() {
            return deferred.getId();
        }

        /**
         * The registry's own Holder.Reference once registration has run (DeferredHolder hashes by key while vanilla
         * references hash by identity, so mixing them breaks map lookups such as LivingEntity#hasEffect). Before
         * registration, the DeferredHolder itself (resolved lazily by whoever holds it).
         */
        @Override
        @SuppressWarnings("unchecked")
        public Holder<T> holder() {
            return (Holder<T>) (Holder<?>) deferred.getDelegate();
        }
    }
}
