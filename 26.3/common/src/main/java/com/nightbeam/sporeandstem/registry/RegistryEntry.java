package com.nightbeam.sporeandstem.registry;

import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;

import java.util.function.Supplier;

/** A registered object. {@link #get()} is only valid once the loader has run registration. */
public interface RegistryEntry<T> extends Supplier<T> {

    Identifier id();

    Holder<T> holder();
}
