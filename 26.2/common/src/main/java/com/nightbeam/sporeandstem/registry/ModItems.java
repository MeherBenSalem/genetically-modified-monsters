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
import net.minecraft.world.item.component.Consumable;
import net.minecraft.world.item.equipment.ArmorType;
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
    public static final RegistryEntry<Item> LUMEN_SPORES = item("lumen_spores", () -> new Item(Keys.itemProps()));
    public static final RegistryEntry<Item> MYCELIAL_THREAD = item("mycelial_thread", () -> new Item(Keys.itemProps()));
    public static final RegistryEntry<Item> MYCOLEATHER = item("mycoleather", () -> new Item(Keys.itemProps()));
    public static final RegistryEntry<Item> BOUNCECAP_GEL = item("bouncecap_gel", () -> new Item(Keys.itemProps()));
    public static final RegistryEntry<Item> MYCELIAL_CORE = item("mycelial_core",
            () -> new Item(Keys.itemProps().rarity(Rarity.UNCOMMON)));
    public static final RegistryEntry<Item> TRUFFLE = item("truffle", () -> new Item(Keys.itemProps().food(ModFoods.TRUFFLE.get(), ModFoods.TRUFFLE.eat().get())));
    public static final RegistryEntry<Item> FRUITING_HEART = item("fruiting_heart",
            () -> new FruitingHeartItem(Keys.itemProps().stacksTo(16).rarity(Rarity.UNCOMMON)));
    public static final RegistryEntry<Item> SPORE_HEART = item("spore_heart",
            () -> new Item(Keys.itemProps().stacksTo(16).rarity(Rarity.EPIC).fireResistant()));

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
    public static final RegistryEntry<Item> FORAGING_KNIFE = item("foraging_knife", () -> new ForagingKnifeItem(ForagingKnifeItem.properties(Keys.itemProps())));
    public static final RegistryEntry<Item> SPORE_BOMB = item("spore_bomb", () -> new SporeBombItem(Keys.itemProps().stacksTo(16)));
    public static final RegistryEntry<Item> MYCOLEATHER_HOOD = armor("mycoleather_hood", ArmorType.HELMET);
    public static final RegistryEntry<Item> MYCOLEATHER_TUNIC = armor("mycoleather_tunic", ArmorType.CHESTPLATE);
    public static final RegistryEntry<Item> MYCOLEATHER_LEGGINGS = armor("mycoleather_leggings", ArmorType.LEGGINGS);
    public static final RegistryEntry<Item> MYCOLEATHER_BOOTS = armor("mycoleather_boots", ArmorType.BOOTS);
    public static final RegistryEntry<Item> BLOOMREAVER = item("bloomreaver",
            () -> new BloomreaverItem(Keys.itemProps().rarity(Rarity.EPIC).fireResistant()
                    .sword(BloomreaverItem.TIER, 4.0F, -2.4F)));
    public static final RegistryEntry<Item> CROWN_OF_THE_BLOOM = item("crown_of_the_bloom",
            () -> new CrownOfTheBloomItem(Keys.itemProps().rarity(Rarity.EPIC).fireResistant()
                    .humanoidArmor(ModArmorMaterials.BLOOM, ArmorType.HELMET).durability(600)));

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
            Keys.building("spore_glob", () -> new Item(Keys.itemProps())));

    private ModItems() {
    }

    public static void init() {
        for (RegistryEntry<? extends Block> block : ModBlocks.WITH_ITEMS) {
            String name = block.id().getPath();
            BLOCK_ITEMS.add(Services.REGISTRAR.register(Registries.ITEM, name,
                    Keys.building(name, () -> new BlockItem(block.get(), Keys.itemProps().useBlockDescriptionPrefix()))));
        }
        // Fungi first, then every other block, then the rest in declaration order.
        TAB.addAll(9, BLOCK_ITEMS);
    }

    private static <T extends Item> RegistryEntry<T> item(String name, Supplier<T> factory) {
        RegistryEntry<T> entry = Services.REGISTRAR.register(Registries.ITEM, name, Keys.building(name, factory));
        TAB.add(entry);
        return entry;
    }

    private static RegistryEntry<Item> fungus(RegistryEntry<Block> block, @Nullable ModFoods.Food food) {
        return item(block.id().getPath(), () -> {
            Item.Properties properties = Keys.itemProps().useBlockDescriptionPrefix();
            if (food != null) {
                properties.food(food.get(), food.eat().get());
            }
            return new BlockItem(block.get(), properties);
        });
    }

    private static RegistryEntry<Item> food(String name, ModFoods.Food food, int stack, boolean drink, boolean cures) {
        return item(name, () -> {
            Item.Properties properties = Keys.itemProps().stacksTo(stack);
            Consumable consumable = drink ? food.drink().get() : food.eat().get();
            if (food.remainder() != null) {
                properties.usingConvertsTo(food.remainder());
            }
            return new FungalFoodItem(properties.food(food.get(), consumable), drink, cures);
        });
    }

    private static RegistryEntry<Item> armor(String name, ArmorType type) {
        return item(name, () -> new MycoleatherArmorItem(type, Keys.itemProps().humanoidArmor(ModArmorMaterials.MYCOLEATHER, type)));
    }

    /**
     * Spawn eggs carry their own textures since 1.21.5; the two colours are kept here as the palette the generated
     * egg textures are drawn from.
     */
    /** The colours are read by the resource port (tools/assets/ss/ports/v26_2.py) into the egg's item tints. */
    private static RegistryEntry<Item> egg(String name, Supplier<? extends EntityType<? extends Mob>> type, int base, int spots) {
        return item(name + "_spawn_egg", () -> new SpawnEggItem(Keys.itemProps().spawnEgg(type.get())));
    }
}
