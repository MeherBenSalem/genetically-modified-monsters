package com.nightbeam.sporeandstem.registry;

import com.nightbeam.sporeandstem.block.BouncecapCapBlock;
import com.nightbeam.sporeandstem.block.CultivationLogBlock;
import com.nightbeam.sporeandstem.block.FungusBlock;
import com.nightbeam.sporeandstem.block.GiantPuffballBlock;
import com.nightbeam.sporeandstem.block.GlowcapCapBlock;
import com.nightbeam.sporeandstem.block.GlowcapGillsBlock;
import com.nightbeam.sporeandstem.block.InkcapCapBlock;
import com.nightbeam.sporeandstem.block.MycelialSoilBlock;
import com.nightbeam.sporeandstem.block.MycelialVeilBlock;
import com.nightbeam.sporeandstem.block.MycelialVeilPlantBlock;
import com.nightbeam.sporeandstem.block.ShelfFungusBlock;
import com.nightbeam.sporeandstem.block.VeilBulbs;
import com.nightbeam.sporeandstem.block.WoodBlocks;
import com.nightbeam.sporeandstem.content.CultivationFungus;
import com.nightbeam.sporeandstem.content.FungusWood;
import com.nightbeam.sporeandstem.platform.Services;
import com.nightbeam.sporeandstem.worldgen.ModConfiguredFeatures;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.FlowerPotBlock;
import net.minecraft.world.level.block.HugeMushroomBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Every block. Block items are made in {@link ModItems} from {@link #WITH_ITEMS}, in registration order (which is
 * also the creative tab order for blocks).
 */
public final class ModBlocks {
    /** Blocks that get a plain block item, in order. */
    public static final List<RegistryEntry<? extends Block>> WITH_ITEMS = new ArrayList<>();
    /** Blocks drawn in the cutout layer (Fabric needs this list; NeoForge reads render_type from the models). */
    public static final List<RegistryEntry<? extends Block>> CUTOUT = new ArrayList<>();
    /** Flower pots and the fungus they hold. */
    public static final Map<RegistryEntry<? extends Block>, RegistryEntry<? extends Block>> POTTED = new LinkedHashMap<>();
    /** Axe stripping: stem → stripped stem, hyphae → stripped hyphae. */
    public static final Map<RegistryEntry<? extends Block>, RegistryEntry<? extends Block>> STRIPPABLES = new LinkedHashMap<>();
    public static final Map<FungusWood, WoodSet> WOOD = new EnumMap<>(FungusWood.class);

    // ---- Small fungi (the item is the mushroom itself) ------------------------------------------------------------
    public static final RegistryEntry<Block> GLOWCAP = fungus("glowcap", ModConfiguredFeatures.HUGE_GLOWCAP,
            Block.box(4, 0, 4, 12, 10, 12), MapColor.COLOR_CYAN, 9);
    public static final RegistryEntry<Block> BOUNCECAP = fungus("bouncecap", ModConfiguredFeatures.HUGE_BOUNCECAP,
            Block.box(3, 0, 3, 13, 9, 13), MapColor.COLOR_PINK, 0);
    public static final RegistryEntry<Block> INKCAP = fungus("inkcap", ModConfiguredFeatures.HUGE_INKCAP,
            Block.box(5, 0, 5, 11, 13, 11), MapColor.COLOR_LIGHT_GRAY, 0);
    public static final RegistryEntry<Block> MOREL = fungus("morel", null,
            Block.box(5, 0, 5, 11, 11, 11), MapColor.TERRACOTTA_BROWN, 0);
    public static final RegistryEntry<Block> CHANTERELLE = fungus("chanterelle", null,
            Block.box(4, 0, 4, 12, 8, 12), MapColor.GOLD, 0);
    public static final RegistryEntry<Block> DEATHCAP = fungus("deathcap", null,
            Block.box(4, 0, 4, 12, 10, 12), MapColor.TERRACOTTA_LIGHT_GREEN, 0);
    public static final RegistryEntry<Block> FROSTCAP = fungus("frostcap", null,
            Block.box(5, 0, 5, 11, 9, 11), MapColor.ICE, 0);
    public static final RegistryEntry<Block> EMBERSTOOL = fungus("emberstool", null,
            Block.box(5, 0, 5, 11, 9, 11), MapColor.COLOR_ORANGE, 7);
    public static final RegistryEntry<Block> PUFFBALL = fungus("puffball", null,
            Block.box(4, 0, 4, 12, 7, 12), MapColor.SNOW, 0);

    // ---- Wood sets ---------------------------------------------------------------------------------------------
    public static final WoodSet GLOWCAP_WOOD = woodSet(FungusWood.GLOWCAP,
            props -> new GlowcapCapBlock(props.lightLevel(state -> 10)));
    public static final WoodSet BOUNCECAP_WOOD = woodSet(FungusWood.BOUNCECAP, BouncecapCapBlock::new);
    public static final WoodSet INKCAP_WOOD = woodSet(FungusWood.INKCAP, InkcapCapBlock::new);
    public static final RegistryEntry<Block> GLOWCAP_CAP = GLOWCAP_WOOD.cap();
    public static final RegistryEntry<Block> BOUNCECAP_CAP = BOUNCECAP_WOOD.cap();
    public static final RegistryEntry<Block> INKCAP_CAP = INKCAP_WOOD.cap();

    public static final RegistryEntry<Block> GLOWCAP_GILLS = cutout(withItem(register("glowcap_gills",
            () -> new GlowcapGillsBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_CYAN).noCollission()
                    .strength(0.2F).sound(SoundType.SHROOMLIGHT).lightLevel(state -> 14).noOcclusion()
                    .pushReaction(PushReaction.DESTROY)))));

    // ---- Other fungal blocks -----------------------------------------------------------------------------------
    public static final RegistryEntry<Block> SHELF_FUNGUS = cutout(withItem(register("shelf_fungus",
            () -> new ShelfFungusBlock(BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_ORANGE)
                    .strength(0.4F).sound(SoundType.FUNGUS).noOcclusion().randomTicks()
                    .pushReaction(PushReaction.DESTROY)))));
    public static final RegistryEntry<Block> MYCELIAL_VEIL = cutout(withItem(register("mycelial_veil",
            () -> new MycelialVeilBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOL).randomTicks()
                    .noCollission().instabreak().sound(SoundType.WEEPING_VINES).lightLevel(VeilBulbs.light(10))
                    .pushReaction(PushReaction.DESTROY)))));
    public static final RegistryEntry<Block> MYCELIAL_VEIL_PLANT = cutout(register("mycelial_veil_plant",
            () -> new MycelialVeilPlantBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOL)
                    .noCollission().instabreak().sound(SoundType.WEEPING_VINES).lightLevel(VeilBulbs.light(10))
                    .pushReaction(PushReaction.DESTROY))));
    public static final RegistryEntry<Block> GIANT_PUFFBALL = withItem(register("giant_puffball",
            () -> new GiantPuffballBlock(BlockBehaviour.Properties.of().mapColor(MapColor.SNOW).strength(0.5F)
                    .sound(SoundType.WOOL))));
    public static final RegistryEntry<Block> TRUFFLE_SOIL = withItem(register("truffle_soil",
            () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.DIRT).strength(0.6F)
                    .sound(SoundType.ROOTED_DIRT))));
    public static final RegistryEntry<Block> MYCELIAL_SOIL = withItem(register("mycelial_soil",
            () -> new MycelialSoilBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_GRAY).strength(0.6F)
                    .sound(SoundType.ROOTED_DIRT).randomTicks())));
    public static final RegistryEntry<Block> GLOWCAP_LANTERN = cutout(withItem(register("glowcap_lantern",
            () -> new LanternBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_CYAN).forceSolidOn()
                    .strength(1.5F).sound(SoundType.SHROOMLIGHT).lightLevel(state -> 15).noOcclusion()
                    .pushReaction(PushReaction.DESTROY)))));
    public static final RegistryEntry<Block> CULTIVATION_LOG = cutout(withItem(register("cultivation_log",
            () -> new CultivationLogBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(1.5F)
                    .sound(SoundType.WOOD).noOcclusion().randomTicks().ignitedByLava()
                    .lightLevel(ModBlocks::cultivationLight)))));

    // ---- Potted fungi ------------------------------------------------------------------------------------------
    static {
        for (RegistryEntry<Block> fungus : List.of(GLOWCAP, BOUNCECAP, INKCAP, MOREL, CHANTERELLE, DEATHCAP, FROSTCAP,
                EMBERSTOOL, PUFFBALL)) {
            potted(fungus);
        }
    }

    private ModBlocks() {
    }

    public static void init() {
    }

    // ---- Helpers -----------------------------------------------------------------------------------------------

    private static <T extends Block> RegistryEntry<T> register(String name, Supplier<T> factory) {
        return Services.REGISTRAR.register(Registries.BLOCK, name, factory);
    }

    private static <T extends Block> RegistryEntry<T> withItem(RegistryEntry<T> entry) {
        WITH_ITEMS.add(entry);
        return entry;
    }

    private static <T extends Block> RegistryEntry<T> cutout(RegistryEntry<T> entry) {
        CUTOUT.add(entry);
        return entry;
    }

    private static RegistryEntry<Block> fungus(String name, @Nullable ResourceKey<ConfiguredFeature<?, ?>> huge,
                                               VoxelShape shape, MapColor color, int light) {
        // The item is made in ModItems (some fungi are edible); fungi are not in WITH_ITEMS.
        return cutout(register(name, () -> new FungusBlock(huge, shape, BlockBehaviour.Properties.of().mapColor(color)
                .noCollission().instabreak().randomTicks().sound(SoundType.FUNGUS)
                .offsetType(BlockBehaviour.OffsetType.XZ).lightLevel(state -> light)
                .pushReaction(PushReaction.DESTROY))));
    }

    private static void potted(RegistryEntry<Block> fungus) {
        String name = "potted_" + fungus.id().getPath();
        RegistryEntry<Block> pot = cutout(register(name, () -> {
            int light = fungus.get().defaultBlockState().getLightEmission();
            return new FlowerPotBlock(fungus.get(), BlockBehaviour.Properties.of().instabreak().noOcclusion()
                    .lightLevel(state -> light).pushReaction(PushReaction.DESTROY));
        }));
        POTTED.put(pot, fungus);
    }

    private static int cultivationLight(BlockState state) {
        int stage = state.getValue(CultivationLogBlock.STAGE);
        return switch (state.getValue(CultivationLogBlock.FUNGUS)) {
            case GLOWCAP -> stage >= 2 ? 4 + stage * 2 : 0;
            case EMBERSTOOL -> stage >= 2 ? 2 + stage : 0;
            default -> 0;
        };
    }

    private static boolean never(BlockState state, BlockGetter level, BlockPos pos, EntityType<?> type) {
        return false;
    }

    private static WoodSet woodSet(FungusWood wood, java.util.function.Function<BlockBehaviour.Properties, ? extends HugeMushroomBlock> capFactory) {
        String w = wood.id();
        MapColor planksColor = wood.planksColor();
        RegistryEntry<Block> cap = withItem(register(w + "_cap", () -> capFactory.apply(BlockBehaviour.Properties.of()
                .mapColor(wood.capColor()).instrument(NoteBlockInstrument.BASS).strength(0.3F).sound(SoundType.WART_BLOCK))));
        RegistryEntry<Block> stem = withItem(register(w + "_stem", () -> new RotatedPillarBlock(stemProps(wood))));
        RegistryEntry<Block> strippedStem = withItem(register("stripped_" + w + "_stem", () -> new RotatedPillarBlock(stemProps(wood))));
        RegistryEntry<Block> hyphae = withItem(register(w + "_hyphae", () -> new RotatedPillarBlock(stemProps(wood))));
        RegistryEntry<Block> strippedHyphae = withItem(register("stripped_" + w + "_hyphae", () -> new RotatedPillarBlock(stemProps(wood))));
        RegistryEntry<Block> planks = withItem(register(w + "_planks", () -> new Block(BlockBehaviour.Properties.of()
                .mapColor(planksColor).instrument(NoteBlockInstrument.BASS).strength(2.0F, 3.0F).sound(SoundType.NETHER_WOOD))));
        RegistryEntry<Block> stairs = withItem(register(w + "_stairs", () -> new WoodBlocks.Stairs(planks.get().defaultBlockState(),
                BlockBehaviour.Properties.ofFullCopy(planks.get()))));
        RegistryEntry<Block> slab = withItem(register(w + "_slab", () -> new SlabBlock(BlockBehaviour.Properties.ofFullCopy(planks.get()))));
        RegistryEntry<Block> fence = withItem(register(w + "_fence", () -> new FenceBlock(BlockBehaviour.Properties.of()
                .mapColor(planksColor).forceSolidOn().instrument(NoteBlockInstrument.BASS).strength(2.0F, 3.0F)
                .sound(SoundType.NETHER_WOOD))));
        RegistryEntry<Block> fenceGate = withItem(register(w + "_fence_gate", () -> new FenceGateBlock(wood.woodType(),
                BlockBehaviour.Properties.of().mapColor(planksColor).forceSolidOn().instrument(NoteBlockInstrument.BASS)
                        .strength(2.0F, 3.0F))));
        RegistryEntry<Block> door = cutout(withItem(register(w + "_door", () -> new WoodBlocks.Door(wood.setType(),
                BlockBehaviour.Properties.of().mapColor(planksColor).instrument(NoteBlockInstrument.BASS).strength(3.0F)
                        .noOcclusion().pushReaction(PushReaction.DESTROY)))));
        RegistryEntry<Block> trapdoor = cutout(withItem(register(w + "_trapdoor", () -> new WoodBlocks.Trapdoor(wood.setType(),
                BlockBehaviour.Properties.of().mapColor(planksColor).instrument(NoteBlockInstrument.BASS).strength(3.0F)
                        .noOcclusion().isValidSpawn(ModBlocks::never)))));
        RegistryEntry<Block> button = withItem(register(w + "_button", () -> new WoodBlocks.Button(wood.setType(), 30,
                BlockBehaviour.Properties.of().noCollission().strength(0.5F).pushReaction(PushReaction.DESTROY))));
        RegistryEntry<Block> pressurePlate = withItem(register(w + "_pressure_plate", () -> new WoodBlocks.PressurePlate(wood.setType(),
                BlockBehaviour.Properties.of().mapColor(planksColor).forceSolidOn().instrument(NoteBlockInstrument.BASS)
                        .noCollission().strength(0.5F).pushReaction(PushReaction.DESTROY))));
        STRIPPABLES.put(stem, strippedStem);
        STRIPPABLES.put(hyphae, strippedHyphae);
        WoodSet set = new WoodSet(wood, cap, stem, strippedStem, hyphae, strippedHyphae, planks, stairs, slab, fence,
                fenceGate, door, trapdoor, button, pressurePlate);
        WOOD.put(wood, set);
        return set;
    }

    private static BlockBehaviour.Properties stemProps(FungusWood wood) {
        return BlockBehaviour.Properties.of().mapColor(wood.stemColor()).instrument(NoteBlockInstrument.BASS)
                .strength(2.0F).sound(SoundType.STEM);
    }

    /** One fungus wood's building set. */
    public record WoodSet(FungusWood wood, RegistryEntry<Block> cap, RegistryEntry<Block> stem,
                          RegistryEntry<Block> strippedStem, RegistryEntry<Block> hyphae,
                          RegistryEntry<Block> strippedHyphae, RegistryEntry<Block> planks, RegistryEntry<Block> stairs,
                          RegistryEntry<Block> slab, RegistryEntry<Block> fence, RegistryEntry<Block> fenceGate,
                          RegistryEntry<Block> door, RegistryEntry<Block> trapdoor, RegistryEntry<Block> button,
                          RegistryEntry<Block> pressurePlate) {
    }

    /** Every fungus a Cultivation Log can be inoculated with, for reference by the client and data code. */
    public static CultivationFungus[] cultivationFungi() {
        return CultivationFungus.values();
    }
}
