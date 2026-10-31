package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.item.BloomreaverItem;
import com.nightbeam.sporeandstem.item.CrownOfTheBloomItem;
import com.nightbeam.sporeandstem.item.ForagingKnifeItem;
import com.nightbeam.sporeandstem.item.FruitingHeartItem;
import com.nightbeam.sporeandstem.item.FungalFoodItem;
import com.nightbeam.sporeandstem.item.MycoleatherArmorItem;
import com.nightbeam.sporeandstem.item.SporeBombItem;
import com.nightbeam.sporeandstem.platform.Services;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.level.block.Block;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/** Every item. {@link #TAB} is the creative tab order. */
public final class ModItems {
    /** Creative tab order. Block items for {@link ModBlocks#WITH_ITEMS} are inserted after the fungi. */
    public static final List<RegistryEntry<? extends Item>> TAB = new ArrayList<>();
    private static final List<RegistryEntry<? extends Item>> BLOCK_ITEMS = new ArrayList<>();

    // ---- Fungi (placeable, most are edible) ----------------------------------------------------------------------
    public static final RegistryEntry<Item> GLOWCAP = fungus(ModBlocks.GLOWCAP, ModFoods.GLOWCAP);
    public static final RegistryEntry<Item> BOUNCECAP = fungus(ModBlocks.BOUNCECAP, ModFoods.BOUNCECAP);
    public static final RegistryEntry<Item> INKCAP = fungus(ModBlocks.INKCAP, null);
    public static final RegistryEntry<Item> MOREL = fungus(ModBlocks.MOREL, ModFoods.MOREL);
    public static final RegistryEntry<Item> CHANTERELLE = fungus(ModBlocks.CHANTERELLE, ModFoods.CHANTERELLE);
    public static final RegistryEntry<Item> DEATHCAP = fungus(ModBlocks.DEATHCAP, ModFoods.DEATHCAP);
    public static final RegistryEntry<Item> FROSTCAP = fungus(ModBlocks.FROSTCAP, ModFoods.FROSTCAP);
    public static final RegistryEntry<Item> EMBERSTOOL = fungus(ModBlocks.EMBERSTOOL, ModFoods.EMBERSTOOL);
    public static final RegistryEntry<Item> PUFFBALL = fungus(ModBlocks.PUFFBALL, ModFoods.PUFFBALL);

    // ---- Materials -----------------------------------------------------------------------------------------------
    public static final RegistryEntry<Item> LUMEN_SPORES = item("lumen_spores", () -> new Item(new Item.Properties()));
    public static final RegistryEntry<Item> MYCELIAL_THREAD = item("mycelial_thread", () -> new Item(new Item.Properties()));
    public static final RegistryEntry<Item> MYCOLEATHER = item("mycoleather", () -> new Item(new Item.Properties()));
    public static final RegistryEntry<Item> BOUNCECAP_GEL = item("bouncecap_gel", () -> new Item(new Item.Properties()));
    public static final RegistryEntry<Item> MYCELIAL_CORE = item("mycelial_core",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final RegistryEntry<Item> TRUFFLE = item("truffle", () -> new Item(new Item.Properties().food(ModFoods.TRUFFLE.get())));
    public static final RegistryEntry<Item> FRUITING_HEART = item("fruiting_heart",
            () -> new FruitingHeartItem(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));
    public static final RegistryEntry<Item> SPORE_HEART = item("spore_heart",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.EPIC).fireResistant()));

    // ---- Food --------------------------------------------------------------------------------------------------
    public static final RegistryEntry<Item> ROASTED_MOREL = food("roasted_morel", ModFoods.ROASTED_MOREL, 64, false, false);
    public static final RegistryEntry<Item> CHANTERELLE_TOAST = food("chanterelle_toast", ModFoods.CHANTERELLE_TOAST, 64, false, false);
    public static final RegistryEntry<Item> GLOWCAP_SOUP = food("glowcap_soup", ModFoods.GLOWCAP_SOUP, 1, false, false);
    public static final RegistryEntry<Item> BOUNCECAP_JELLY = food("bouncecap_jelly", ModFoods.BOUNCECAP_JELLY, 16, true, false);
    public static final RegistryEntry<Item> FROSTCAP_TEA = food("frostcap_tea", ModFoods.FROSTCAP_TEA, 16, true, false);
    public static final RegistryEntry<Item> EMBER_SKEWER = food("ember_skewer", ModFoods.EMBER_SKEWER, 64, false, false);
    public static final RegistryEntry<Item> TRUFFLE_STEW = food("truffle_stew", ModFoods.TRUFFLE_STEW, 1, false, false);
    public static final RegistryEntry<Item> FORAGERS_STEW = food("foragers_stew", ModFoods.FORAGERS_STEW, 1, false, true);
    public static final RegistryEntry<Item> ANTIFUNGAL_TONIC = food("antifungal_tonic", ModFoods.ANTIFUNGAL_TONIC, 16, true, true);

    // ---- Tools, weapons and armor -----------------------------------------------------------------------------
    public static final RegistryEntry<Item> FORAGING_KNIFE = item("foraging_knife", () -> new ForagingKnifeItem(new Item.Properties()));
    public static final RegistryEntry<Item> SPORE_BOMB = item("spore_bomb", () -> new SporeBombItem(new Item.Properties().stacksTo(16)));
    public static final RegistryEntry<Item> MYCOLEATHER_HOOD = armor("mycoleather_hood", ArmorItem.Type.HELMET);
    public static final RegistryEntry<Item> MYCOLEATHER_TUNIC = armor("mycoleather_tunic", ArmorItem.Type.CHESTPLATE);
    public static final RegistryEntry<Item> MYCOLEATHER_LEGGINGS = armor("mycoleather_leggings", ArmorItem.Type.LEGGINGS);
    public static final RegistryEntry<Item> MYCOLEATHER_BOOTS = armor("mycoleather_boots", ArmorItem.Type.BOOTS);
    public static final RegistryEntry<Item> BLOOMREAVER = item("bloomreaver",
            () -> new BloomreaverItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant()));
    public static final RegistryEntry<Item> CROWN_OF_THE_BLOOM = item("crown_of_the_bloom",
            () -> new CrownOfTheBloomItem(new Item.Properties().rarity(Rarity.EPIC).fireResistant().durability(600)));

    // ---- Spawn eggs --------------------------------------------------------------------------------------------
    public static final RegistryEntry<Item> SPORELING_SPAWN_EGG = egg("sporeling", ModEntities.SPORELING::get, 0xE9E0C9, 0x3FC7C0);
    public static final RegistryEntry<Item> TRUFFLER_SPAWN_EGG = egg("truffler", ModEntities.TRUFFLER::get, 0x6B4E3D, 0x7A8F4F);
    public static final RegistryEntry<Item> GLOWMOTH_SPAWN_EGG = egg("glowmoth", ModEntities.GLOWMOTH::get, 0x2F4858, 0x6BF2E3);
    public static final RegistryEntry<Item> BLOATSHROOM_SPAWN_EGG = egg("bloatshroom", ModEntities.BLOATSHROOM::get, 0xEDE6D6, 0x8FA36B);
    public static final RegistryEntry<Item> SHAMBLER_SPAWN_EGG = egg("shambler", ModEntities.SHAMBLER::get, 0x5B4A3F, 0xB9A58A);
    public static final RegistryEntry<Item> SPOREMAW_SPAWN_EGG = egg("sporemaw", ModEntities.SPOREMAW::get, 0x4C3A52, 0xC27BA0);
    public static final RegistryEntry<Item> MIMICAP_SPAWN_EGG = egg("mimicap", ModEntities.MIMICAP::get, 0xB0302A, 0xF2E8D5);
    public static final RegistryEntry<Item> MYCELIARCH_SPAWN_EGG = egg("myceliarch", ModEntities.MYCELIARCH::get, 0x3B2E3A, 0x48E5C2);

    /** Projectile sprite only; not in the creative tab. */
    public static final RegistryEntry<Item> SPORE_GLOB = Services.REGISTRAR.register(Registries.ITEM, "spore_glob",
            () -> new Item(new Item.Properties()));

    private ModItems() {
    }

    public static void init() {
        for (RegistryEntry<? extends Block> block : ModBlocks.WITH_ITEMS) {
            BLOCK_ITEMS.add(Services.REGISTRAR.register(Registries.ITEM, block.id().getPath(),
                    () -> new BlockItem(block.get(), new Item.Properties())));
        }
        // Fungi first, then every other block, then the rest in declaration order.
        TAB.addAll(9, BLOCK_ITEMS);
    }

    private static <T extends Item> RegistryEntry<T> item(String name, Supplier<T> factory) {
        RegistryEntry<T> entry = Services.REGISTRAR.register(Registries.ITEM, name, factory);
        TAB.add(entry);
        return entry;
    }

    private static RegistryEntry<Item> fungus(RegistryEntry<Block> block, @Nullable Supplier<FoodProperties> food) {
        return item(block.id().getPath(), () -> {
            Item.Properties properties = new Item.Properties();
            if (food != null) {
                properties.food(food.get());
            }
            return new BlockItem(block.get(), properties);
        });
    }

    private static RegistryEntry<Item> food(String name, Supplier<FoodProperties> food, int stack, boolean drink, boolean cures) {
        return item(name, () -> new FungalFoodItem(new Item.Properties().food(food.get()).stacksTo(stack), drink, cures));
    }

    private static RegistryEntry<Item> armor(String name, ArmorItem.Type type) {
        return item(name, () -> new MycoleatherArmorItem(type, new Item.Properties().durability(type.getDurability(14))));
    }

    private static RegistryEntry<Item> egg(String name, Supplier<? extends EntityType<? extends Mob>> type, int base, int spots) {
        return item(name + "_spawn_egg", () -> new SpawnEggItem(type.get(), base, spots, new Item.Properties()));
    }
}
