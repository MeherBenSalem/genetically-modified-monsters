package com.nightbeam.sporeandstem.platform;

import com.nightbeam.sporeandstem.SporeAndStem;
import com.nightbeam.sporeandstem.platform.services.IPlatformHelper;
import com.nightbeam.sporeandstem.platform.services.IRegistrar;

import java.util.ServiceLoader;

/** Loads the loader-specific implementations declared in {@code META-INF/services}. */
public final class Services {
    public static final IPlatformHelper PLATFORM = load(IPlatformHelper.class);
    public static final IRegistrar REGISTRAR = load(IRegistrar.class);

    private Services() {
    }

    public static <T> T load(Class<T> clazz) {
        T service = ServiceLoader.load(clazz, Services.class.getClassLoader())
                .findFirst()
                .orElseThrow(() -> new NullPointerException("Failed to load service for " + clazz.getName()));
        SporeAndStem.LOGGER.debug("Loaded {} for service {}", service, clazz);
        return service;
    }
}
