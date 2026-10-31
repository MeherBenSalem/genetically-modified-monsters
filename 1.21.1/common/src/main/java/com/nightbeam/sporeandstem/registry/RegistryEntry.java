package com.nightbeam.sporeandstem.registry;

import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceLocation;

import java.util.function.Supplier;

/** A registered object. {@link #get()} is only valid once the loader has run registration. */
public interface RegistryEntry<T> extends Supplier<T> {

    ResourceLocation id();

    Holder<T> holder();
}
