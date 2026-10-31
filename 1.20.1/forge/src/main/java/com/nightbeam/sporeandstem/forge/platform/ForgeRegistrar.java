package com.nightbeam.sporeandstem.forge.platform;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.platform.services.IRegistrar;
import com.nightbeam.sporeandstem.registry.RegistryEntry;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

/** One {@link DeferredRegister} per vanilla registry; {@link #registerAll} hooks them onto the mod bus. */
public class ForgeRegistrar implements IRegistrar {
    private static final Map<ResourceKey<?>, DeferredRegister<?>> REGISTERS = new LinkedHashMap<>();

    @Override
    @SuppressWarnings("unchecked")
    public <R, T extends R> RegistryEntry<T> register(ResourceKey<? extends Registry<R>> registryKey, String name, Supplier<T> factory) {
        DeferredRegister<R> register = (DeferredRegister<R>) REGISTERS.computeIfAbsent(registryKey,
                key -> DeferredRegister.create((ResourceKey<Registry<R>>) registryKey, SporeAndStem.MOD_ID));
        return new Entry<>(register.register(name, factory));
    }

    public static void registerAll(IEventBus modBus) {
        REGISTERS.values().forEach(register -> register.register(modBus));
    }

    private record Entry<R, T extends R>(RegistryObject<T> object) implements RegistryEntry<T> {
        @Override
        public T get() {
            return object.get();
        }

        @Override
        public ResourceLocation id() {
            return object.getId();
        }

        /** The registry's own Holder.Reference; only valid once registration has run. */
        @Override
        public Holder<T> holder() {
            return object.getHolder().orElseThrow(() -> new IllegalStateException("Not registered yet: " + object.getId()));
        }
    }
}
