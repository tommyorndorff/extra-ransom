/* Salamanders of Western North Carolina — data.
   Taxonomy follows SSAR Standard Names 9th ed. (2025) and Amphibian Species of the World 6.2.
   Elevations are generalized for WNC from regional accounts, species descriptions and revisions; they are a
   guide to where to look, not range limits. Ranges: 2 = present, 1 = marginal/peripheral, absent keys = absent. */
window.SAL = (function () {
  const families = [
    { id: "cryptobranchidae", name: "Cryptobranchidae", common: "giant salamanders", color: "#7a4e2d" },
    { id: "proteidae", name: "Proteidae", common: "waterdogs and mudpuppies", color: "#9a6b3b" },
    { id: "ambystomatidae", name: "Ambystomatidae", common: "mole salamanders", color: "#5b5f8a" },
    { id: "salamandridae", name: "Salamandridae", common: "newts", color: "#e8741e" },
    { id: "plethodontidae", name: "Plethodontidae", common: "lungless salamanders", color: "#2e5a66" }
  ];
  const habitats = [
    { id: "river", name: "Rivers and large streams", short: "River" },
    { id: "channel", name: "Stream channel (in-stream)", short: "Stream channel" },
    { id: "bank", name: "Stream banks and splash zone", short: "Stream bank" },
    { id: "seep", name: "Seeps, springs and headwaters", short: "Seep / spring" },
    { id: "forest", name: "Forest floor, away from water", short: "Forest floor" },
    { id: "outcrop", name: "Rock outcrops and crevices", short: "Rock crevice" },
    { id: "pool", name: "Breeding pools and wetlands", short: "Pools" }
  ];
  const basins = [
    { id: "TN", short: "Tennessee basin", name: "Tennessee basin (Hiwassee, Little Tennessee, French Broad, Watauga)" },
    { id: "NEW", short: "New River (Ohio basin)", name: "New River (Ohio basin)" },
    { id: "ATL", short: "Atlantic slope", name: "Atlantic slope (Savannah, Broad, Catawba, Yadkin)" }
  ];
  const ranges = [
    { id: "smokies", name: "Great Smokies", note: "Great Smoky Mountains, NC side: Swain and Haywood counties" },
    { id: "unicoi", name: "Unicoi, Snowbird & Cheoah", note: "Graham and Cherokee counties, including Cheoah Bald" },
    { id: "nantahala", name: "Nantahala & Cowee", note: "Macon, Clay and Swain counties" },
    { id: "balsams", name: "Plott & Great Balsams", note: "Haywood, Jackson and Transylvania counties" },
    { id: "escarpment", name: "Highlands & SW escarpment", note: "Highlands Plateau and escarpment gorges of Jackson, Macon and Transylvania counties" },
    { id: "hng", name: "Hickory Nut Gorge & Blue Ridge front", note: "Henderson, Rutherford and southern Buncombe counties" },
    { id: "bald", name: "Bald Mtns & French Broad valley", note: "Madison County and the French Broad corridor" },
    { id: "black", name: "Black Mtns & Craggies", note: "Yancey and northern Buncombe counties" },
    { id: "roan", name: "Roan & Unakas", note: "Mitchell and Avery counties along the TN line" },
    { id: "grandfather", name: "Grandfather & Linville", note: "Avery, Watauga, Caldwell and Burke counties" },
    { id: "newriver", name: "New River plateau", note: "Ashe, Alleghany and northern Watauga counties" },
    { id: "foothills", name: "Foothills & South Mtns", note: "Lower Blue Ridge front: Burke, McDowell, Rutherford, Polk, Wilkes and Surry counties" }
  ];
  const zones = [
    { name: "Oak and cove hardwoods", from: 150, to: 1000, fill: "var(--zone-cove)" },
    { name: "Northern hardwoods", from: 1000, to: 1400, fill: "var(--zone-north)" },
    { name: "Spruce–fir, highest peaks", from: 1400, to: 2100, fill: "var(--zone-spruce)" }
  ];
  const refPeaks = [
    { name: "Asheville", m: 650 },
    { name: "Mount Mitchell", m: 2037 }
  ];

  const ALL = { smokies: 2, unicoi: 2, nantahala: 2, balsams: 2, escarpment: 2, hng: 2, bald: 2, black: 2, roan: 2, grandfather: 2, newriver: 2, foothills: 2 };
  const species = [
    /* ---------- Cryptobranchidae ---------- */
    {
      id: "alleganiensis", family: "cryptobranchidae", sci: "Cryptobranchus alleganiensis", auth: "(Sonnini de Manoncourt & Latreille, 1801)",
      common: "Eastern hellbender", habitat: "river", elev: [400, 950], basins: ["TN", "NEW"],
      range: "Larger rivers and streams of the Hiwassee, Little Tennessee, French Broad (including the Pigeon and the Nolichucky headwaters), Watauga and New basins. Absent from every Atlantic-slope basin.",
      microhabitat: "Swift, cool, low-conductivity reaches with large, flat, partly embedded cover rocks that open downstream; larvae use unembedded cobble and gravel.",
      size: "Adults typically 40–45 cm TL; can exceed 60 cm.",
      repro: "External fertilization in a cavity under a large rock, late August to September in NC. The male guards 200–500 eggs that hatch in 10–12 weeks. Larvae keep external gills about 1.5–2 years.",
      id_notes: "Unmistakable: dorsoventrally flattened, wrinkled lateral skin folds, tiny lidless eyes, one pair of gill slits in adults. The only similar animal is the mudpuppy, which keeps bushy external gills.",
      notes: "49 occupied stream segments known in WNC (SE CASC 2026). See the hellbender section for life history, listing history and post-Helene status.",
      tax: "Tennessee-basin animals carry <i>C. alleganiensis</i> s.s. The New–Kanawha lineage, which includes NW North Carolina, is a deep unnamed lineage (Hime 2017; SSAR 2025).",
      nc: "SC", fed: "Proposed Endangered, range-wide (89 FR 100934, 13 Dec 2024); final rule overdue", fedShort: "Fed. PE",
      grank: "G3T2", srank: "S3", iucn: "VU (2022)", statusNote: "Missouri DPS is federally Endangered (2021) but does not occur in NC. Critical habitat ruled not prudent.",
      photo: "hellbender", ranges: { smokies: 1, unicoi: 2, nantahala: 2, balsams: 1, escarpment: 1, bald: 2, black: 1, roan: 2, grandfather: 1, newriver: 2 }
    },
    /* ---------- Proteidae ---------- */
    {
      id: "maculosus", family: "proteidae", sci: "Necturus maculosus", auth: "(Rafinesque, 1818)",
      common: "Common mudpuppy", habitat: "river", elev: [400, 800], basins: ["TN", "NEW"],
      range: "Rivers and reservoirs of the Tennessee drainages (French Broad, Hiwassee, Little Tennessee); a single New River record (Williams & Corey 2007).",
      microhabitat: "Larger rivers and impoundments; active year-round, including under ice. Eggs attached to the underside of rocks.",
      size: "About 20–33 cm TL.",
      repro: "Permanently aquatic and paedomorphic. The female guards eggs attached beneath a cover rock.",
      id_notes: "Bushy maroon external gills, four toes on each foot, a dark stripe through the eye. Often caught by winter anglers.",
      tax: "Name contested. ASW, following Chabarria et al. (2018), assigns these populations to <i>N. louisianensis</i> Viosca, 1938. SSAR (2025) retains <i>N. maculosus</i> and notes that Hiwassee waterdogs include at least two species, one sister to <i>N. lewisi</i> (Nelson et al. 2017).",
      formerly: "N. louisianensis (per ASW)",
      nc: "SC", grank: "G5", srank: "S2", iucn: "LC (2015)",
      ranges: { unicoi: 2, nantahala: 1, bald: 2, newriver: 1 }
    },
    /* ---------- Ambystomatidae ---------- */
    {
      id: "maculatum", family: "ambystomatidae", sci: "Ambystoma maculatum", auth: "(Shaw, 1802)",
      common: "Spotted salamander", habitat: "pool", elev: [200, 1500], basins: ["TN", "NEW", "ATL"],
      range: "Throughout WNC wherever fishless pools persist, from foothills to high-elevation wetlands.",
      microhabitat: "Fossorial in hardwood forest; breeds in fishless ephemeral and semi-permanent pools.",
      size: "About 15–20 cm TL.",
      repro: "Migrates to pools on rainy nights from late winter to early spring. Firm, globular egg masses, often with symbiotic green algae (<i>Oophila</i>).",
      id_notes: "Two irregular rows of round yellow to orange dorsal spots on a dark ground.",
      photo: "spotted", ranges: ALL
    },
    {
      id: "opacum", family: "ambystomatidae", sci: "Ambystoma opacum", auth: "(Gravenhorst, 1807)",
      common: "Marbled salamander", habitat: "pool", elev: [200, 1000], basins: ["TN", "ATL"],
      range: "Mostly foothills and lower valleys; scattered montane records (Williams et al. 2014).",
      microhabitat: "Dry pool basins and floodplain depressions that fill in autumn and winter.",
      size: "About 9–11 cm TL.",
      repro: "Autumn breeder. The female lays eggs on land in a dry basin and broods them until autumn rains flood the nest.",
      id_notes: "Stocky, with bold white (male) or gray (female) crossbands on black.",
      photo: "marbled", ranges: { smokies: 1, unicoi: 1, nantahala: 1, escarpment: 1, hng: 2, bald: 1, foothills: 2 }
    },
    /* ---------- Salamandridae ---------- */
    {
      id: "viridescens", family: "salamandridae", sci: "Notophthalmus viridescens", auth: "(Rafinesque, 1820)",
      common: "Red-spotted newt", habitat: "pool", elev: [200, 1900], basins: ["TN", "NEW", "ATL"],
      range: "Throughout WNC. Red efts wander forest floors to the summits after summer rain.",
      microhabitat: "Adults in ponds and quiet pools; terrestrial efts in moist forest.",
      size: "About 7–10 cm TL.",
      repro: "Aquatic eggs and larvae. A terrestrial red eft stage lasts several years before the animal returns to water as an olive-green adult with red spots.",
      id_notes: "Efts are bright orange with black-ringed red spots and rough, dry-looking skin. They are tetrodotoxin-defended, which is why they walk in the open by day.",
      tax: "WNC populations are <i>N. v. viridescens</i>.",
      photo: "red-eft", ranges: ALL
    },
    /* ---------- Plethodontidae: Desmognathus, stream channel ---------- */
    {
      id: "intermedius", family: "plethodontidae", sci: "Desmognathus intermedius", auth: "(Pope, 1928)",
      common: "Western shovel-nosed salamander", habitat: "channel", elev: [300, 1500], basins: ["TN"], endemic: "SA",
      range: "Nantahala, Cheoah, Oconaluftee, Tuckasegee, Pigeon and French Broad drainages. Rare or absent in the upper Little Tennessee and Tuckasegee.",
      microhabitat: "Fully aquatic in riffles and runs, under cobbles in fast, well-oxygenated water.",
      size: "SVL 28–85 mm; the largest of the shovel-nosed species.",
      repro: "Aquatic larvae; larval period about 3 years.",
      id_notes: "Wedge-shaped, flattened head; small eyes; venter pale. Vomerine teeth present in both sexes, unlike <i>D. aureatus</i>.",
      tax: "Split from <i>D. marmoratus</i> by Pyron & Beamer (2023); <i>D. melanius</i> Martof, 1956 is a synonym. The shovel-nosed form evolved twice in <i>Desmognathus</i>, once in the Pisgah clade (<i>intermedius</i>) and once in the Nantahala clade (<i>aureatus</i>).",
      formerly: "D. marmoratus; Leurognathus",
      photo: "inat-intermedius", ranges: { smokies: 2, unicoi: 2, nantahala: 2, balsams: 2, escarpment: 1, bald: 1 }
    },
    {
      id: "marmoratus", family: "plethodontidae", sci: "Desmognathus marmoratus", auth: "(Moore, 1899)",
      common: "Northern shovel-nosed salamander", habitat: "channel", elev: [450, 1600], basins: ["TN", "ATL"], endemic: "SA",
      range: "Blue Ridge northeast of the Pigeon River: Watauga, Nolichucky and South Fork Holston drainages, plus the upper Broad and upper Catawba on the Atlantic slope.",
      microhabitat: "Fully aquatic in riffles of clear, rocky streams.",
      size: "SVL about 30–75 mm.",
      repro: "Aquatic larvae; a clutch has been recorded on 6 August.",
      id_notes: "Shorter head than the other two shovel-nosed species. Type locality: a rocky pool on the south flank of Grandfather Mountain, Avery County, at about 1,070 m (3,500 ft).",
      tax: "Restricted sense after Pyron & Beamer (2023).",
      formerly: "Leurognathus marmoratus",
      photo: "shovel-nosed", ranges: { hng: 1, black: 2, roan: 2, grandfather: 2, foothills: 1 }
    },
    {
      id: "amphileucus", family: "plethodontidae", sci: "Desmognathus amphileucus", auth: "Bishop, 1941",
      common: "Southern black-bellied salamander", habitat: "channel", elev: [375, 1500], basins: ["TN", "ATL"], endemic: "SA",
      range: "Southwestern NC south of the Smokies and mostly west of the French Broad, on both sides of the divide (Savannah headwaters included).",
      microhabitat: "Stream channels and edges, under large rocks in splash zones and riffles.",
      size: "About 10–18 cm TL.",
      repro: "Aquatic larvae; larval period 2–4 years.",
      id_notes: "Large, robust, with a black venter and two rows of pale spots on the sides. Separating it from the other black-bellied species usually takes mtDNA.",
      tax: "Resurrected by Pyron & Beamer (2022). The familiar name <i>D. quadramaculatus</i> turned out to be a junior synonym of <i>D. fuscus</i>, and the black-bellied concept dissolved into several species in two distantly related clades.",
      formerly: "D. quadramaculatus",
      photo: "inat-amphileucus", ranges: { unicoi: 2, nantahala: 2, balsams: 1, escarpment: 2 }
    },
    {
      id: "gvnigeusgwotli", family: "plethodontidae", sci: "Desmognathus gvnigeusgwotli", auth: "Pyron & Beamer, 2022",
      common: "Smoky Mountains black-bellied salamander", habitat: "channel", elev: [450, 1200], basins: ["TN"], endemic: "SA",
      range: "Great Smoky Mountains, with isolated records in the Unicoi, Great Balsam and Bald Mountains.",
      microhabitat: "Stream channels, chiefly at lower elevations in the park.",
      size: "About 10–18 cm TL.",
      repro: "Aquatic larvae with a multi-year larval period.",
      id_notes: "Black-bellied habitus; identification in sympatry with <i>D. mavrokoilius</i> generally needs genetic data.",
      notes: "The epithet is Cherokee for &ldquo;black belly.&rdquo; It was the first new vertebrate described from the Smokies All Taxa Biodiversity Inventory. Shaw et al. (2025) found it co-occurring with <i>D. mavrokoilius</i> across more of the park than expected.",
      formerly: "D. quadramaculatus",
      photo: "black-bellied", ranges: { smokies: 2, unicoi: 1, balsams: 1 }
    },
    {
      id: "mavrokoilius", family: "plethodontidae", sci: "Desmognathus mavrokoilius", auth: "Pyron & Beamer, 2022",
      common: "Pisgah black-bellied salamander", habitat: "channel", elev: [400, 1700], basins: ["TN"], endemic: "SA",
      range: "NC Blue Ridge from the eastern Smokies and southeastern Great Balsams north to Mount Rogers. Whether it reaches Atlantic-slope drainages has not been confirmed.",
      microhabitat: "Stream channels and splash zones.",
      size: "About 10–18 cm TL.",
      repro: "Aquatic larvae with a multi-year larval period.",
      id_notes: "Black-bellied habitus. The epithet is Greek for &ldquo;black belly.&rdquo;",
      notes: "Type locality: Dixon Creek on the south slope of Grandfather Mountain, Caldwell County.",
      formerly: "D. quadramaculatus",
      photo: "inat-mavrokoilius", ranges: { smokies: 1, balsams: 2, escarpment: 1, bald: 2, black: 2, roan: 2, grandfather: 2, newriver: 1 }
    },
    {
      id: "folkertsi", family: "plethodontidae", sci: "Desmognathus folkertsi", auth: "Camp, Tilley, Austin & Marshall, 2002",
      common: "Dwarf black-bellied salamander", habitat: "channel", elev: [600, 1100], basins: ["TN"], endemic: "SA",
      range: "In NC known only from Hiwassee tributaries in Clay County (first state record: Rothermel et al. 2007). The core range is in northern Georgia.",
      microhabitat: "Small, rocky, high-gradient streams.",
      size: "Smaller than other black-bellied species.",
      repro: "Aquatic larvae.",
      id_notes: "A small black-bellied form; sister to <i>D. aureatus</i> in the Nantahala clade.",
      nc: "SC", grank: "G2G3", srank: "S1", iucn: "LC (2023)",
      photo: "inat-folkertsi", ranges: { nantahala: 1 }
    },
    /* ---------- Desmognathus, banks and seeps ---------- */
    {
      id: "monticola", family: "plethodontidae", sci: "Desmognathus monticola", auth: "Dunn, 1916",
      common: "Northern seal salamander", habitat: "bank", elev: [250, 1500], basins: ["TN", "NEW", "ATL"],
      range: "Widespread across WNC on both sides of the divide.",
      microhabitat: "Stream banks and the splash zone, under rocks and logs at the water's edge, often in burrows.",
      size: "About 8–13 cm TL.",
      repro: "Aquatic larvae; females brood eggs in streambank cavities.",
      id_notes: "Strongly bicolored: dark, reticulated dorsum sharply set off from a pale, unmarked venter. The tail is laterally compressed and knife-edged.",
      tax: "All WNC populations are <i>D. monticola</i> s.s.; the southern lineage is <i>D. cheaha</i> (Pyron et al. 2023), which does not occur in WNC.",
      photo: "seal", ranges: { ...ALL, foothills: 1 }
    },
    {
      id: "tilleyi", family: "plethodontidae", sci: "Desmognathus tilleyi", auth: "Pyron & Beamer, 2023",
      common: "Max Patch dusky salamander", habitat: "bank", elev: [400, 1300], basins: ["TN"], endemic: "SA",
      range: "Southern Bald Mountains from Lemon Gap to the Pigeon River (Madison and Haywood counties), plus Smokies foothills.",
      microhabitat: "Streamsides and seeps.",
      size: "Dusky-sized.",
      repro: "Aquatic larvae.",
      id_notes: "Not reliably separable from other duskies in the field; locality and genetics.",
      tax: "Corresponds to Tilley et al.'s (2013) &ldquo;Lemon Gap&rdquo; form, previously treated within <i>D. conanti</i>.",
      formerly: "D. conanti",
      watch: true, grank: "G2", srank: "S1S2", statusNote: "NCNHP Significantly Rare; no legal status.",
      photo: "inat-tilleyi", ranges: { smokies: 1, bald: 2 }
    },
    {
      id: "campi", family: "plethodontidae", sci: "Desmognathus campi", auth: "Pyron & Beamer, 2023",
      common: "Savannah dusky salamander", habitat: "bank", elev: [600, 900], basins: ["TN"],
      range: "In WNC only in upper French Broad headwaters of Transylvania County. The rest of the range is on the Atlantic Coastal Plain.",
      microhabitat: "Streamsides.",
      size: "Dusky-sized.",
      repro: "Aquatic larvae.",
      id_notes: "Genetic identification.",
      tax: "WNC populations are a sublineage possibly of hybrid origin (Pyron & Beamer 2023).",
      formerly: "D. conanti / D. fuscus",
      watch: true, grank: "G3", srank: "S1S2", statusNote: "NCNHP Significantly Rare; no legal status.",
      photo: "inat-campi", ranges: { escarpment: 2 }
    },
    {
      id: "fuscus", family: "plethodontidae", sci: "Desmognathus fuscus", auth: "(Green, 1818)",
      common: "Northern dusky salamander", habitat: "bank", elev: [300, 1100], basins: ["NEW", "ATL"],
      range: "Northwestern NC.",
      microhabitat: "Streamsides, seeps and springs.",
      size: "About 6–11 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "A light line runs from the eye to the angle of the jaw, as in most <i>Desmognathus</i>. The tail is keeled and triangular in cross-section.",
      tax: "Holbrook's <i>quadramaculata</i> is a junior synonym of this species (Pyron & Beamer 2022). The species was restricted by Pyron & Beamer (2023).",
      photo: "inat-fuscus", ranges: { grandfather: 1, newriver: 2, foothills: 1 }
    },
    {
      id: "lycos", family: "plethodontidae", sci: "Desmognathus lycos", auth: "Pyron & Beamer, 2023",
      common: "Wolf dusky salamander", habitat: "bank", elev: [250, 800], basins: ["ATL"],
      range: "Blue Ridge foothills of central NC.",
      microhabitat: "Streamsides.",
      size: "Dusky-sized.",
      repro: "Aquatic larvae.",
      id_notes: "Shares mtDNA haplotypes with <i>D. carolinensis</i>; genetic identification.",
      formerly: "D. fuscus / D. conanti",
      photo: "inat-lycos", ranges: { hng: 1, foothills: 2 }
    },
    {
      id: "santeetlah", family: "plethodontidae", sci: "Desmognathus santeetlah", auth: "Tilley, 1981",
      common: "Santeetlah dusky salamander", habitat: "seep", elev: [900, 1900], basins: ["TN"], endemic: "SA",
      range: "Great Smokies, Great Balsams and Unicoi Mountains.",
      microhabitat: "Seeps, springs and small headwater streams.",
      size: "About 7–9.5 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "The keeled tail separates it from <i>D. balsameus</i> and <i>D. adatsihi</i>. Often greenish-yellow below.",
      tax: "Petranka (1998) did not recognize it; it is recognized by SSAR and ASW.",
      photo: "inat-santeetlah", ranges: { smokies: 2, unicoi: 2, balsams: 2 }
    },
    {
      id: "aeneus", family: "plethodontidae", sci: "Desmognathus aeneus", auth: "Brown & Bishop, 1947",
      common: "Seepage salamander", habitat: "seep", elev: [400, 1100], basins: ["TN", "ATL"],
      range: "Extreme southwestern NC.",
      microhabitat: "Leaf litter and moss at seeps and small streamheads.",
      size: "About 4.4–5.7 cm TL.",
      repro: "Direct development; terrestrial eggs.",
      id_notes: "Tiny, with a coppery dorsal band and a light line from the eye to the jaw. Similar to the pygmy salamanders, but at lower elevations and closely tied to seeps.",
      tax: "At least three unnamed phylogeographic lineages.",
      watch: true, srank: "S3", statusNote: "NCNHP watch list (W-RS); no legal status.",
      photo: "inat-aeneus", ranges: { unicoi: 1, nantahala: 1 }
    },
    {
      id: "perlapsus", family: "plethodontidae", sci: "Desmognathus perlapsus", auth: "Neill, 1950",
      common: "Chattooga dusky salamander", habitat: "seep", elev: [600, 1500], basins: ["TN", "ATL"], endemic: "SA",
      range: "Alarka and Cowee Mountains, and the Savannah headwaters, including the Highlands Plateau.",
      microhabitat: "Wet rock faces, seepage crevices and splash zones.",
      size: "SVL 22–56 mm.",
      repro: "Aquatic larvae.",
      id_notes: "Some Cowee and Highlands animals have red cheek patches, which can be confused with <i>D. imitator</i> or juvenile <i>Plethodon</i>.",
      tax: "Resurrected from the <i>D. ocoee</i> complex by Pyron & Beamer (2022).",
      formerly: "D. ocoee",
      photo: "inat-perlapsus", ranges: { nantahala: 2, escarpment: 2 }
    },
    /* ---------- Desmognathus, forest floor ---------- */
    {
      id: "ocoee", family: "plethodontidae", sci: "Desmognathus ocoee", auth: "Nicholls, 1949",
      common: "Ocoee salamander", habitat: "forest", elev: [800, 1650], basins: ["TN"], endemic: "SA",
      range: "In WNC, the Nantahala and Unicoi Mountains.",
      microhabitat: "Forest floor, seeps and wet rock faces.",
      size: "SVL 15–54 mm.",
      repro: "Aquatic larvae.",
      id_notes: "Variable. Lineage E animals sometimes have red, orange or yellow leg patches that suggest <i>P. shermani</i>.",
      tax: "Restricted sense after Pyron & Beamer (2022), which split the complex into <i>ocoee</i>, <i>adatsihi</i>, <i>balsameus</i> and <i>perlapsus</i>.",
      photo: "ocoee", ranges: { unicoi: 2, nantahala: 2 }
    },
    {
      id: "adatsihi", family: "plethodontidae", sci: "Desmognathus adatsihi", auth: "Pyron & Beamer, 2022",
      common: "Cherokee mountain dusky salamander", habitat: "forest", elev: [1200, 2000], basins: ["TN"], endemic: "SA",
      range: "Great Smokies and Plott Balsams, at high elevation.",
      microhabitat: "Forest floor far from water; all genetic samples were from above 1,500 m.",
      size: "SVL 23–50 mm.",
      repro: "Aquatic larvae.",
      id_notes: "A straight-edged dorsal stripe, which never occurs in <i>D. imitator</i>. On the Rough Ridge transect, <i>imitator</i> occupies 1,340–1,490 m and <i>adatsihi</i> 1,540–1,630 m.",
      tax: "The name comes from Cherokee for &ldquo;mother of all,&rdquo; a nod to the lineage's hybrid mitochondrial origin.",
      formerly: "D. ocoee",
      photo: "inat-adatsihi", ranges: { smokies: 2, balsams: 1 }
    },
    {
      id: "balsameus", family: "plethodontidae", sci: "Desmognathus balsameus", auth: "Pyron & Beamer, 2022",
      common: "Great Balsams mountain dusky salamander", habitat: "forest", elev: [1000, 1900], basins: ["TN"], endemic: "NC",
      range: "Great Balsam Mountains in Haywood, Jackson and Transylvania counties; possibly western Buncombe and Henderson.",
      microhabitat: "Forest floor at mid to high elevations.",
      size: "SVL 19–47 mm.",
      repro: "Aquatic larvae.",
      id_notes: "Wavy-edged dorsal stripe; no tail keel.",
      formerly: "D. ocoee",
      watch: true, srank: "SNR", statusNote: "NC endemic. NCNHP watch list (W-PK); not yet ranked.",
      photo: "inat-balsameus", ranges: { balsams: 2 }
    },
    {
      id: "imitator", family: "plethodontidae", sci: "Desmognathus imitator", auth: "Dunn, 1927",
      common: "Imitator salamander", habitat: "forest", elev: [450, 2000], basins: ["TN"], endemic: "SA",
      range: "Great Smokies at all elevations, plus the Balsams. The Waterrock Knob population is tracked separately by NCNHP.",
      microhabitat: "Forest floor and seeps.",
      size: "About 7–9 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "Red, orange or yellow cheek patches, the putative mimicry of <i>P. jordani</i> that gives it its name. Check for the light eye-to-jaw line and hind legs larger than the forelegs, which mark it as a <i>Desmognathus</i>.",
      watch: true, grank: "G3G4", srank: "S3", iucn: "NT (2022)", statusNote: "NCNHP watch list; the Waterrock Knob population is ranked S1?.",
      photo: "inat-imitator", ranges: { smokies: 2, balsams: 1 }
    },
    {
      id: "carolinensis", family: "plethodontidae", sci: "Desmognathus carolinensis", auth: "Dunn, 1916",
      common: "Carolina mountain dusky salamander", habitat: "forest", elev: [700, 2030], basins: ["TN", "ATL"], endemic: "SA",
      range: "From Linville Falls, McKinney Gap and Iron Mountain Gap south to the Pigeon River, including the Black Mountains.",
      microhabitat: "Forest floor and seeps, to the summit of Mount Mitchell.",
      size: "About 7–11 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "Variable dorsal pattern; hybridizes with <i>D. orestes</i> at the McKinney Gap contact (Mead & Tilley 2000).",
      formerly: "D. ochrophaeus",
      photo: "inat-carolinensis", ranges: { hng: 1, bald: 2, black: 2, roan: 1, grandfather: 1 }
    },
    {
      id: "orestes", family: "plethodontidae", sci: "Desmognathus orestes", auth: "Tilley & Mahoney, 1996",
      common: "Blue Ridge dusky salamander", habitat: "forest", elev: [700, 1800], basins: ["TN", "NEW", "ATL"], endemic: "SA",
      range: "Northeast of Linville Falls and McKinney Gap, and of the Toms and Clark Creeks near Iron Mountain Gap, north to Floyd County, Virginia.",
      microhabitat: "Forest floor and seeps.",
      size: "About 7–10 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "Field-separable from <i>D. carolinensis</i> mainly by locality.",
      tax: "SSAR notes two cryptic units. The Unaka Mountain population shows hybridization with <i>D. ochrophaeus</i> (Pyron et al. 2022).",
      formerly: "D. ochrophaeus",
      photo: "inat-orestes", ranges: { roan: 2, grandfather: 2, newriver: 2 }
    },
    {
      id: "organi", family: "plethodontidae", sci: "Desmognathus organi", auth: "Crespi, Browne & Rissler, 2010",
      common: "Northern pygmy salamander", habitat: "forest", elev: [1100, 2030], basins: ["TN", "ATL"], endemic: "SA",
      range: "North of the French Broad: Black Mountains, Grandfather, Roan, and north to Mount Rogers and Whitetop in Virginia.",
      microhabitat: "Forest floor, moss and spruce–fir litter at high elevation.",
      size: "About 4–5 cm TL; among the smallest salamanders in North America.",
      repro: "Direct development.",
      id_notes: "Morphologically cryptic with <i>D. wrighti</i>; the French Broad is the boundary between them. Herringbone dorsal pattern.",
      tax: "Moskwik (2014) documented shifts in its elevational limits since Hairston's surveys.",
      formerly: "D. wrighti",
      watch: true, grank: "G3", srank: "S2S3", statusNote: "NCNHP Significantly Rare; no legal status. SWAP high priority.",
      photo: "inat-organi", ranges: { black: 2, roan: 2, grandfather: 2 }
    },
    {
      id: "wrighti", family: "plethodontidae", sci: "Desmognathus wrighti", auth: "King, 1936",
      common: "Pygmy salamander", habitat: "forest", elev: [950, 2000], basins: ["TN"], endemic: "SA",
      range: "South of the French Broad: Smokies, Plott and Great Balsams, and the Cowee, Nantahala and Unicoi Mountains (there at 950–1,400 m).",
      microhabitat: "Forest floor, mostly above 1,400 m; climbs vegetation on wet nights.",
      size: "About 4–5 cm TL.",
      repro: "Direct development.",
      id_notes: "Tiny, with a coppery herringbone dorsal stripe.",
      tax: "Restricted to south of the French Broad since <i>D. organi</i> was split off. There may be a distinct lineage in the southern Nantahalas.",
      watch: true, grank: "G3", srank: "S3", statusNote: "NCNHP Significantly Rare; no legal status.",
      photo: "pygmy", ranges: { smokies: 2, unicoi: 2, nantahala: 2, balsams: 2 }
    },
    /* ---------- Plethodon ---------- */
    {
      id: "jordani", family: "plethodontidae", sci: "Plethodon jordani", auth: "Blatchley, 1901",
      common: "Red-cheeked salamander", habitat: "forest", elev: [900, 2025], basins: ["TN"], endemic: "SA",
      range: "Great Smoky Mountains only, at mid to high elevations.",
      microhabitat: "Mesic forest floor in northern hardwoods and spruce–fir.",
      size: "About 8.5–18 cm TL.",
      repro: "Direct development; the female guards a terrestrial or subterranean nest.",
      id_notes: "Slate-black with red cheek patches and no dorsal spotting.",
      notes: "The species at the center of Hairston's Smokies competition experiments. Restricted to the Smokies since Highton & Peabody (2000).",
      watch: true, srank: "S3", iucn: "NT", statusNote: "NCNHP watch list (W-PK); no legal status.",
      photo: "red-cheeked", ranges: { smokies: 2 }
    },
    {
      id: "metcalfi", family: "plethodontidae", sci: "Plethodon metcalfi", auth: "Brimley, 1912",
      common: "Southern gray-cheeked salamander", habitat: "forest", elev: [500, 1950], basins: ["TN", "ATL"], endemic: "SA",
      range: "Balsam Mountains and the Highlands region of southwestern NC, into South Carolina and Georgia.",
      microhabitat: "Mesic hardwood and spruce–fir forest floor.",
      size: "About 8.5–17 cm TL.",
      repro: "Direct development.",
      id_notes: "Plain gray-black with paler cheeks and no red.",
      notes: "Forms a three-way contact with <i>P. jordani</i> and <i>P. teyahalee</i> at Balsam Mountain, with mitochondrial–nuclear discordance (Chatfield et al. 2010).",
      tax: "Hairston's Balsam Mountains &ldquo;<i>jordani</i>&rdquo; populations are, under current taxonomy, probably this species.",
      formerly: "P. jordani",
      photo: "gray-cheeked", ranges: { nantahala: 1, balsams: 2, escarpment: 2 }
    },
    {
      id: "shermani", family: "plethodontidae", sci: "Plethodon shermani", auth: "Stejneger, 1906",
      common: "Red-legged salamander", habitat: "forest", elev: [850, 1650], basins: ["TN"], endemic: "SA",
      range: "Nantahala and Unicoi Mountains and nearby ranges, into Towns County, Georgia.",
      microhabitat: "Mesic forest floor at mid to high elevations.",
      size: "About 9–17 cm TL.",
      repro: "Direct development. Studied extensively for its courtship pheromones (plethodontid receptivity factor).",
      id_notes: "Red to orange upper legs on a black body.",
      notes: "Forms an elevational hybrid zone with <i>P. teyahalee</i> in the Nantahalas. At Coweeta, the share of pure <i>shermani</i> at high elevations fell as mean annual temperature rose over 16 years (Walls 2009).",
      formerly: "P. jordani",
      watch: false, iucn: "NT (2022)",
      photo: "red-legged", ranges: { unicoi: 2, nantahala: 2 }
    },
    {
      id: "cheoah", family: "plethodontidae", sci: "Plethodon cheoah", auth: "Highton & Peabody, 2000",
      common: "Cheoah Bald salamander", habitat: "forest", elev: [855, 1545], basins: ["TN"], endemic: "NC",
      range: "Cheoah Bald and adjacent ridges, Graham and Swain counties. One of the narrowest ranges of any salamander in the region.",
      microhabitat: "Mesic forest floor.",
      size: "Gray-cheeked size, about 9–16 cm TL.",
      repro: "Direct development.",
      id_notes: "Dark, with small white dorsal spots; identified mainly by locality.",
      formerly: "P. jordani",
      watch: true, grank: "G1G2", srank: "S1", iucn: "VU (2022)", statusNote: "NC endemic. NCNHP Significantly Rare; no legal status.",
      photo: "inat-cheoah", ranges: { unicoi: 2 }
    },
    {
      id: "amplus", family: "plethodontidae", sci: "Plethodon amplus", auth: "Highton & Peabody, 2000",
      common: "Blue Ridge gray-cheeked salamander", habitat: "forest", elev: [700, 1400], basins: ["TN", "ATL"], endemic: "NC",
      range: "Buncombe, Henderson and Rutherford counties, on the Blue Ridge front around Hickory Nut Gorge.",
      microhabitat: "Mesic forest floor and rocky slopes.",
      size: "Gray-cheeked size.",
      repro: "Direct development.",
      id_notes: "Dark gray with pale cheeks; identified by locality.",
      tax: "The elevation range in ASW (1,109–1,116 m) appears to be an error; the range here is generalized.",
      formerly: "P. jordani",
      watch: true, grank: "G2", srank: "S1", iucn: "EN (2022)", statusNote: "NC endemic. NCNHP Significantly Rare; no legal status.",
      photo: "inat-amplus", ranges: { hng: 2 }
    },
    {
      id: "meridianus", family: "plethodontidae", sci: "Plethodon meridianus", auth: "Highton & Peabody, 2000",
      common: "South Mountain gray-cheeked salamander", habitat: "forest", elev: [540, 830], basins: ["ATL"], endemic: "NC",
      range: "South Mountains of Burke, Cleveland and Rutherford counties.",
      microhabitat: "Cool, mesic north-facing coves; habitat associations in Radomski et al. (2024).",
      size: "Gray-cheeked size.",
      repro: "Direct development.",
      id_notes: "Identified by locality; the only gray-cheeked in the South Mountains.",
      formerly: "P. jordani",
      watch: true, grank: "G2", srank: "S1", iucn: "EN (2022)", statusNote: "NC endemic. NCNHP Significantly Rare; no legal status.",
      photo: "inat-meridianus", ranges: { foothills: 2 }
    },
    {
      id: "montanus", family: "plethodontidae", sci: "Plethodon montanus", auth: "Highton & Peabody, 2000",
      common: "Northern gray-cheeked salamander", habitat: "forest", elev: [800, 1900], basins: ["TN", "NEW"], endemic: "SA",
      range: "Northeastern Blue Ridge of NC, Tennessee and Virginia; a Buncombe High Top record (Reynolds et al. 2022).",
      microhabitat: "Mesic hardwood and spruce–fir forest floor.",
      size: "Gray-cheeked size.",
      repro: "Direct development.",
      id_notes: "Plain dark gray; identified by locality.",
      formerly: "P. jordani",
      photo: "inat-montanus", ranges: { bald: 2, black: 2, roan: 2, grandfather: 2, newriver: 2 }
    },
    {
      id: "teyahalee", family: "plethodontidae", sci: "Plethodon teyahalee", auth: "Hairston, 1950",
      common: "Southern Appalachian salamander", habitat: "forest", elev: [300, 1300], basins: ["TN", "ATL"], endemic: "SA",
      range: "West of the French Broad, plus Rabun County, Georgia, and upstate South Carolina.",
      microhabitat: "Forest floor at low to middle elevations.",
      size: "About 12–17 cm TL.",
      repro: "Direct development.",
      id_notes: "A large slimy salamander with small white dorsal spots and sometimes red leg spots where it meets <i>P. shermani</i>.",
      notes: "The &ldquo;<i>P. glutinosus</i>&rdquo; of Hairston's competition experiments. Its synonym <i>P. oconaluftee</i> Hairston, 1993 was described from a holotype taken beside FS 140 near the North Fork of the French Broad, Transylvania County, at 930 m. The type series came from a hybrid zone.",
      formerly: "P. glutinosus; P. oconaluftee",
      photo: "inat-teyahalee", ranges: { smokies: 2, unicoi: 2, nantahala: 2, balsams: 1, escarpment: 1 }
    },
    {
      id: "aureolus", family: "plethodontidae", sci: "Plethodon aureolus", auth: "Highton, 1984",
      common: "Tellico salamander", habitat: "forest", elev: [300, 1500], basins: ["TN"], endemic: "SA",
      range: "Unicoi Mountains of NC and Tennessee.",
      microhabitat: "Forest floor.",
      size: "Slimy-salamander size, about 11–16 cm TL.",
      repro: "Direct development.",
      id_notes: "Slimy type with brassy or yellowish dorsal flecking.",
      tax: "Not monophyletic in Fisher-Reid & Wiens (2011).",
      watch: true, grank: "G2G3", srank: "S2", iucn: "DD (2023)", statusNote: "NCNHP Significantly Rare; no legal status.",
      photo: "inat-aureolus", ranges: { unicoi: 2 }
    },
    {
      id: "chattahoochee", family: "plethodontidae", sci: "Plethodon chattahoochee", auth: "Highton, 1989",
      common: "Chattahoochee slimy salamander", habitat: "forest", elev: [400, 1200], basins: ["TN"], endemic: "SA",
      range: "In NC, southeastern Cherokee County only.",
      microhabitat: "Forest floor.",
      size: "Slimy-salamander size.",
      repro: "Direct development.",
      id_notes: "Slimy type with sparse white spotting; identified by locality.",
      tax: "Shows gene flow with <i>P. teyahalee</i> and <i>P. shermani</i> (Pierson et al. 2023). Petranka (1998) did not recognize it.",
      watch: true, grank: "G3", srank: "S1", statusNote: "NCNHP Significantly Rare; no legal status.",
      photo: "inat-chattahoochee", ranges: { nantahala: 1 }
    },
    {
      id: "cylindraceus", family: "plethodontidae", sci: "Plethodon cylindraceus", auth: "(Harlan, 1825)",
      common: "White-spotted slimy salamander", habitat: "forest", elev: [200, 1500], basins: ["TN", "NEW", "ATL"],
      range: "East of the French Broad, on both slopes.",
      microhabitat: "Forest floor, under logs and in rotting wood.",
      size: "About 12–17 cm TL.",
      repro: "Direct development.",
      id_notes: "Black with abundant white or brassy spots. Its skin secretion is famously sticky.",
      formerly: "P. glutinosus",
      photo: "slimy", ranges: { escarpment: 1, hng: 2, bald: 1, black: 2, roan: 2, grandfather: 2, newriver: 2, foothills: 2 }
    },
    {
      id: "cinereus", family: "plethodontidae", sci: "Plethodon cinereus", auth: "(Green, 1818)",
      common: "Eastern red-backed salamander", habitat: "forest", elev: [600, 1700], basins: ["NEW", "TN", "ATL"],
      range: "Mountains of northwestern NC.",
      microhabitat: "Forest floor under cover objects.",
      size: "About 6–10 cm TL.",
      repro: "Direct development.",
      id_notes: "Red-backed and lead-backed morphs. The salt-and-pepper venter separates it from <i>P. serratus</i>, whose dorsal stripe has saw-toothed edges.",
      photo: "red-backed", ranges: { black: 1, roan: 1, grandfather: 2, newriver: 2 }
    },
    {
      id: "serratus", family: "plethodontidae", sci: "Plethodon serratus", auth: "Grobman, 1944",
      common: "Southern red-backed salamander", habitat: "forest", elev: [500, 1400], basins: ["TN"],
      range: "Extreme southwestern NC.",
      microhabitat: "Forest floor, often on drier slopes.",
      size: "About 7–10 cm TL.",
      repro: "Direct development.",
      id_notes: "Narrow red dorsal stripe with serrated edges.",
      photo: "inat-serratus", ranges: { unicoi: 2, nantahala: 2, escarpment: 1 }
    },
    {
      id: "ventralis", family: "plethodontidae", sci: "Plethodon ventralis", auth: "Highton, 1997",
      common: "Southern zigzag salamander", habitat: "forest", elev: [350, 800], basins: ["TN"],
      range: "French Broad valley at low elevations.",
      microhabitat: "Rocky, moist slopes and seeps.",
      size: "About 7–9 cm TL.",
      repro: "Direct development.",
      id_notes: "A wavy, zigzag-edged dorsal stripe and a mottled venter.",
      nc: "SC", grank: "G4", srank: "S2", iucn: "LC (2014)",
      photo: "inat-ventralis", ranges: { bald: 2 }
    },
    {
      id: "richmondi", family: "plethodontidae", sci: "Plethodon richmondi", auth: "Netting & Mittleman, 1938",
      common: "Southern ravine salamander", habitat: "forest", elev: [500, 1100], basins: ["TN", "NEW"],
      range: "Extreme northwestern NC; county-level distribution needs confirmation.",
      microhabitat: "Ravine slopes and talus.",
      size: "About 7.5–11 cm TL.",
      repro: "Direct development.",
      id_notes: "Long and slender, with short legs and fine silvery flecking on a dark body.",
      watch: true, srank: "S3", statusNote: "NCNHP watch list (W-RS); no legal status.",
      photo: "inat-richmondi", ranges: { newriver: 1 }
    },
    {
      id: "jacksoni", family: "plethodontidae", sci: "Plethodon jacksoni", auth: "Newman, 1954",
      common: "Blacksburg salamander", habitat: "forest", elev: [600, 1200], basins: ["NEW"],
      range: "Northwestern NC adjacent to southwestern Virginia; counties need confirmation.",
      microhabitat: "Forest floor and rocky slopes.",
      size: "About 10–15 cm TL.",
      repro: "Direct development.",
      id_notes: "Dark, with paired white or yellowish dorsal spots.",
      tax: "Formerly treated as the NC population of <i>P. wehrlei</i>; elevated by Felix et al. (2019). Kuchta et al. (2024) call for denser sampling. NC listings still use &ldquo;Wehrle's salamander.&rdquo;",
      formerly: "P. wehrlei",
      nc: "T", grank: "G4", srank: "S2", iucn: "LC (2014, as P. wehrlei)", statusNote: "Listed by NCWRC as Wehrle's salamander.",
      photo: "inat-jacksoni", ranges: { newriver: 1 }
    },
    {
      id: "welleri", family: "plethodontidae", sci: "Plethodon welleri", auth: "Walker, 1931",
      common: "Weller's salamander", habitat: "forest", elev: [750, 2000], basins: ["TN", "NEW", "ATL"], endemic: "SA",
      range: "Mount Rogers south to Yancey County: Grandfather, Roan and the Black Mountains.",
      microhabitat: "Spruce–fir and northern hardwood forest floor, often in moss on rocks and under logs.",
      size: "About 5–7.5 cm TL; the smallest <i>Plethodon</i> in NC.",
      repro: "Direct development.",
      id_notes: "Black with brassy or gold dorsal flecking that can coalesce into blotches.",
      notes: "Described by Walker (1931) from high elevation on Grandfather Mountain.",
      nc: "SC", grank: "G3", srank: "S2", iucn: "EN (2004)", statusNote: "SWAP high priority. Spruce–fir dependent and vulnerable to warming.",
      photo: "wellers", ranges: { black: 2, roan: 2, grandfather: 2, newriver: 1 }
    },
    {
      id: "yonahlossee", family: "plethodontidae", sci: "Plethodon yonahlossee", auth: "Dunn, 1917",
      common: "Yonahlossee salamander", habitat: "forest", elev: [300, 1700], basins: ["TN", "NEW", "ATL"], endemic: "SA",
      range: "Blue Ridge of NC, Virginia and Tennessee, including the Hickory Nut Gorge &ldquo;crevice salamander&rdquo; populations.",
      microhabitat: "Rocky forest and talus; the Hickory Nut Gorge form lives in rock crevices.",
      size: "About 11–14 cm TL, rarely to 22 cm.",
      repro: "Direct development.",
      id_notes: "A broad chestnut-red dorsal band and pale gray flanks.",
      tax: "<i>P. longicrus</i> Adler & Dennis, 1962, the crevice salamander of Hickory Nut Gorge, was recognized by Wiens et al. (2006) but returned to synonymy by Highton et al. (2012). Its status is contested. NCWRC lists the crevice salamander separately.",
      watch: true, statusNote: "The Hickory Nut Gorge crevice-salamander population (&ldquo;P. longicrus&rdquo;) is NC Special Concern (NHP S1, G4T1T2Q). The species is otherwise unlisted.",
      photo: "inat-yonahlossee", ranges: { hng: 2, bald: 1, black: 2, roan: 2, grandfather: 2, newriver: 2, foothills: 1 }
    },
    /* ---------- Other plethodontids ---------- */
    {
      id: "aeneusA", family: "plethodontidae", sci: "Aneides aeneus", auth: "(Cope & Packard, 1881)",
      common: "Green salamander", habitat: "outcrop", elev: [300, 1300], basins: ["TN", "ATL"],
      range: "Blue Ridge Escarpment of southwestern NC: rock outcrops in the gorges of Jackson, Macon and Transylvania counties. This is a population disjunct from the Cumberland Plateau core.",
      microhabitat: "Narrow, moist, shaded crevices in rock outcrops; also arboreal.",
      size: "About 8–12.5 cm TL.",
      repro: "Direct development. Eggs hang from crevice ceilings and the female broods them. Breeding is often biennial.",
      id_notes: "Lichen-green patches on a black ground; flattened head and body; square-tipped toes for climbing.",
      tax: "After <i>A. caryaensis</i> was split off, three more lineages remain within nominal <i>A. aeneus</i>. They are recommended as ESUs but are not yet named (Patton et al. 2019).",
      nc: "T", grank: "G3G4", srank: "S2S3", iucn: "NT (2022)", statusNote: "Collection pressure documented. Never publish point localities.",
      photo: "green", ranges: { nantahala: 1, escarpment: 2 }
    },
    {
      id: "caryaensis", family: "plethodontidae", sci: "Aneides caryaensis", auth: "Patton et al., 2019",
      common: "Hickory Nut Gorge green salamander", habitat: "outcrop", elev: [330, 950], basins: ["ATL"], endemic: "NC",
      range: "Hickory Nut Gorge and nearby escarpment in Rutherford, Henderson and Polk counties.",
      microhabitat: "Rock crevices in cove forest.",
      size: "Similar to <i>A. aeneus</i>, with the tail longer than the SVL.",
      repro: "Direct development; the female broods.",
      id_notes: "Smaller, less connected lichen-like green patches than <i>A. aeneus</i>. The two species are allopatric.",
      notes: "Estimated 200–500 animals before Helene. Twenty-five were rescued after the storm into a captive program at the NC Zoo (with TNC, ARC and NCWRC); no captive hatching had been reported as of February 2026.",
      nc: "E", fed: "Under ESA status review (substantial 90-day finding, 89 FR 4884, 25 Jan 2024)", fedShort: "Fed. review",
      grank: "G1", srank: "S1", iucn: "CR (2022)", statusNote: "NC endemic. No 12-month federal finding yet.",
      photo: "inat-caryaensis", ranges: { hng: 2 }
    },
    {
      id: "wilderae", family: "plethodontidae", sci: "Eurycea wilderae", auth: "Dunn, 1920",
      common: "Blue Ridge two-lined salamander", habitat: "bank", elev: [250, 2000], basins: ["TN", "NEW", "ATL"], endemic: "SA",
      range: "Ubiquitous across the mountains, from valley floors to the highest summits.",
      microhabitat: "Stream margins and seeps; adults disperse into the forest in summer.",
      size: "About 6–10 cm TL.",
      repro: "Aquatic larvae; eggs attached under rocks in flowing water.",
      id_notes: "Yellow to orange, with two dark dorsolateral lines. Breeding males have cirri and swollen snouts.",
      notes: "Sympatric with <i>E. cirrigera</i> at lower elevations in places (Camp et al. 2000).",
      photo: "blue-ridge-two-lined", ranges: { ...ALL, foothills: 1 }
    },
    {
      id: "cirrigera", family: "plethodontidae", sci: "Eurycea cirrigera", auth: "(Green, 1831)",
      common: "Southern two-lined salamander", habitat: "bank", elev: [200, 700], basins: ["TN", "ATL"],
      range: "Foothills and lower valleys.",
      microhabitat: "Stream margins and floodplain seeps.",
      size: "About 6.5–10 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "Like <i>E. wilderae</i>, but with broken lines on the tail and a lower-elevation range.",
      photo: "inat-cirrigera", ranges: { unicoi: 1, escarpment: 1, hng: 1, bald: 1, foothills: 2 }
    },
    {
      id: "guttolineata", family: "plethodontidae", sci: "Eurycea guttolineata", auth: "(Holbrook, 1838)",
      common: "Three-lined salamander", habitat: "seep", elev: [200, 700], basins: ["TN", "ATL"],
      range: "Low elevations and foothills.",
      microhabitat: "Floodplain seeps, spring runs and muddy stream margins.",
      size: "About 10–16 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "Yellow, with a dark middorsal stripe plus dark lateral stripes, and a long tail.",
      photo: "three-lined", ranges: { unicoi: 1, nantahala: 1, hng: 1, foothills: 2 }
    },
    {
      id: "longicauda", family: "plethodontidae", sci: "Eurycea longicauda", auth: "(Green, 1818)",
      common: "Eastern long-tailed salamander", habitat: "bank", elev: [400, 900], basins: ["TN"],
      range: "Very limited in NC. Sources disagree on whether the records fall in the extreme west (ASW) or the extreme northwest (herpsofnc.org); check the NC Herp Atlas before relying on either.",
      microhabitat: "Stream margins, seeps and moist rock crevices; also caves elsewhere in its range.",
      size: "About 10–16 cm TL.",
      repro: "Aquatic larvae; eggs laid underground.",
      id_notes: "Yellow-orange with black spots, and vertical herringbone bars on a very long tail.",
      nc: "T", grank: "G5T5", srank: "S1S2", iucn: "LC (2014)", statusNote: "Renamed &ldquo;Eastern long-tailed salamander&rdquo; in the 2024 NC rule.",
      photo: "long-tailed"
    },
    {
      id: "junaluska", family: "plethodontidae", sci: "Eurycea junaluska", auth: "Sever, Dundee & Sullivan, 1976",
      common: "Junaluska salamander", habitat: "river", elev: [450, 900], basins: ["TN"], endemic: "SA",
      range: "Unicoi, Snowbird and Cheoah drainages, and the edge of the Smokies; larger streams and rivers.",
      microhabitat: "Larger, lower-gradient streams. Adults are under rocks and logs near the water.",
      size: "About 8–10 cm TL.",
      repro: "Aquatic larvae in larger streams.",
      id_notes: "Like a two-lined salamander, but with the dorsolateral lines faint or broken and a more robust build.",
      nc: "T", grank: "G2G3", srank: "S1", iucn: "VU (2004)", statusNote: "SWAP high priority.",
      photo: "inat-junaluska", ranges: { smokies: 1, unicoi: 2 }
    },
    {
      id: "porphyriticus", family: "plethodontidae", sci: "Gyrinophilus porphyriticus", auth: "(Green, 1827)",
      common: "Spring salamander", habitat: "seep", elev: [250, 1900], basins: ["TN", "NEW", "ATL"],
      range: "Throughout WNC: <i>G. p. danielsi</i> (Blue Ridge spring salamander) and <i>G. p. dunni</i> (Carolina spring salamander).",
      microhabitat: "Springs, seeps and cold headwater streams.",
      size: "About 11–19 cm TL.",
      repro: "Aquatic larvae with a larval period of several years.",
      id_notes: "Salmon to reddish with a light canthal line from eye to nostril. Eats other salamanders.",
      photo: "spring", ranges: ALL
    },
    {
      id: "ruber", family: "plethodontidae", sci: "Pseudotriton ruber", auth: "(Sonnini de Manoncourt & Latreille, 1801)",
      common: "Red salamander", habitat: "seep", elev: [200, 1500], basins: ["TN", "NEW", "ATL"],
      range: "Throughout WNC: <i>P. r. nitidus</i> (Blue Ridge red), <i>P. r. schencki</i> (black-chinned, southwestern NC) and <i>P. r. ruber</i>.",
      microhabitat: "Springs, seeps and small streams with soft substrate.",
      size: "About 10–16 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "Bright red with irregular black spots and a yellow iris. Older adults darken.",
      photo: "red", ranges: ALL
    },
    {
      id: "montanusP", family: "plethodontidae", sci: "Pseudotriton montanus", auth: "Baird, 1850",
      common: "Mud salamander", habitat: "seep", elev: [200, 600], basins: ["ATL"],
      range: "Foothills on the Atlantic slope.",
      microhabitat: "Muddy seeps and floodplain springs.",
      size: "About 8–19 cm TL.",
      repro: "Aquatic larvae.",
      id_notes: "Like the red salamander, but with a brown iris and fewer, rounder spots.",
      photo: "inat-montanusP", ranges: { hng: 1, escarpment: 1, foothills: 2 }
    },
    {
      id: "scutatum", family: "plethodontidae", sci: "Hemidactylium scutatum", auth: "(Temminck, 1838)",
      common: "Four-toed salamander", habitat: "seep", elev: [250, 1200], basins: ["TN", "NEW", "ATL"],
      range: "Scattered across WNC in sphagnum seeps and bog wetlands.",
      microhabitat: "Sphagnum mats over seeps and small pools.",
      size: "About 5–9 cm TL.",
      repro: "Nests in moss above water; the female broods and larvae drop into the water after hatching. Brief larval period.",
      id_notes: "Four toes on the hind feet, a constriction at the base of the tail, and a white venter with bold black spots.",
      nc: "SC", grank: "G5", srank: "S3", iucn: "LC (2022)",
      photo: "four-toed", ranges: { nantahala: 1, escarpment: 1, hng: 1, black: 1, newriver: 1, foothills: 1 }
    }
  ];

  const refs = [
    "Beane JC, Braswell AL, Mitchell JC, Palmer WM, Harrison JR. 2010. <i>Amphibians and Reptiles of the Carolinas and Virginia</i>, 2nd ed. UNC Press.",
    "Bletz MC et al. 2023. <i>Herpetological Review</i> 54:200–203.",
    "Bodinof Jachowski CM, Hopkins WA. 2018. Loss of catchment-wide riparian forest cover is associated with reduced recruitment in a long-lived amphibian. <i>Biological Conservation</i> 220:215–227. <a href=\"https://doi.org/10.1016/j.biocon.2018.02.012\">doi:10.1016/j.biocon.2018.02.012</a>",
    "Bruce RC. 1996. <i>Copeia</i> 1996:783–790.",
    "Bruce RC. 2013. <i>Copeia</i> 2013:262–267.",
    "Caruso NM, Lips KR. 2013. Truly enigmatic declines in terrestrial salamander populations in Great Smoky Mountains National Park. <i>Diversity and Distributions</i> 19:38–48. <a href=\"https://doi.org/10.1111/j.1472-4642.2012.00938.x\">doi:10.1111/j.1472-4642.2012.00938.x</a>",
    "Caruso NM, Sears MW, Adams DC, Lips KR. 2014. Widespread rapid reductions in body size of adult salamanders in response to climate change. <i>Global Change Biology</i> 20:1751–1759. <a href=\"https://doi.org/10.1111/gcb.12550\">doi:10.1111/gcb.12550</a>",
    "Chatfield MWH, Kozak KH, Fitzpatrick BM, Tucker PK. 2010. <i>Molecular Ecology</i>. <a href=\"https://doi.org/10.1111/j.1365-294X.2010.04796.x\">doi:10.1111/j.1365-294X.2010.04796.x</a>",
    "Connette GM, Crawford JA, Peterman WE. 2015. Climate change and shrinking salamanders: alternative mechanisms for changes in plethodontid salamander body size. <i>Global Change Biology</i> 21:2834–2843. <a href=\"https://doi.org/10.1111/gcb.12883\">doi:10.1111/gcb.12883</a>",
    "Crespi EJ, Browne RA, Rissler LJ. 2010. Taxonomic revision of <i>Desmognathus wrighti</i>. <i>Herpetologica</i> 66:283–295. <a href=\"https://doi.org/10.1655/Herpetologica-D-09-00002.1\">doi:10.1655/Herpetologica-D-09-00002.1</a>",
    "Hairston NG. 1949. The local distribution and ecology of the plethodontid salamanders of the southern Appalachians. <i>Ecological Monographs</i> 19:47–73. <a href=\"https://doi.org/10.2307/1943584\">doi:10.2307/1943584</a>",
    "Hairston NG. 1951. Interspecies competition and its probable influence upon the vertical distribution of Appalachian salamanders of the genus <i>Plethodon</i>. <i>Ecology</i> 32:266–274. <a href=\"https://doi.org/10.2307/1930418\">doi:10.2307/1930418</a>",
    "Hairston NG. 1980. The experimental test of an analysis of field distributions: competition in terrestrial salamanders. <i>Ecology</i> 61:817–826. <a href=\"https://doi.org/10.2307/1936752\">doi:10.2307/1936752</a>",
    "Hairston NG. 1980. Evolution under interspecific competition: field experiments on terrestrial salamanders. <i>Evolution</i> 34:409–420. <a href=\"https://doi.org/10.1111/j.1558-5646.1980.tb04829.x\">doi:10.1111/j.1558-5646.1980.tb04829.x</a>",
    "Hairston NG, Nishikawa KC, Stenhouse SL. 1987. The evolution of competing species of terrestrial salamanders: niche partitioning or interference? <i>Evolutionary Ecology</i> 1:247–262. <a href=\"https://doi.org/10.1007/BF02067555\">doi:10.1007/BF02067555</a>",
    "Hairston NG, Wiley RH, Smith CK, Kneidel KA. 1992. The dynamics of two hybrid zones in Appalachian salamanders of the genus <i>Plethodon</i>. <i>Evolution</i> 46:930–938. <a href=\"https://doi.org/10.1111/j.1558-5646.1992.tb00610.x\">doi:10.1111/j.1558-5646.1992.tb00610.x</a>",
    "Highton R, Peabody RB. 2000. Geographic protein variation and speciation in salamanders of the <i>Plethodon jordani</i> and <i>Plethodon glutinosus</i> complexes in the southern Appalachian Mountains. In Bruce RC et al. (eds), <i>The Biology of Plethodontid Salamanders</i>: 31–93. <a href=\"https://doi.org/10.1007/978-1-4615-4255-1_3\">doi:10.1007/978-1-4615-4255-1_3</a>",
    "Hopkins WA et al. 2023. <i>American Naturalist</i> 202:92–106. <a href=\"https://doi.org/10.1086/724819\">doi:10.1086/724819</a>",
    "Kozak KH, Larson A, Bonett RM, Harmon LJ. 2005. Phylogenetic analysis of ecomorphological divergence, community structure, and diversification rates in dusky salamanders. <i>Evolution</i> 59:2000–2016. <a href=\"https://doi.org/10.1111/j.0014-3820.2005.tb01069.x\">doi:10.1111/j.0014-3820.2005.tb01069.x</a>",
    "Kozak KH, Wiens JJ. 2010. Accelerated rates of climatic-niche evolution underlie rapid species diversification. <i>Ecology Letters</i> 13:1378–1389. <a href=\"https://doi.org/10.1111/j.1461-0248.2010.01530.x\">doi:10.1111/j.1461-0248.2010.01530.x</a>",
    "Milanovich JR, Peterman WE, Nibbelink NP, Maerz JC. 2010. Projected loss of a salamander diversity hotspot as a consequence of projected global climate change. <i>PLoS ONE</i> 5:e12189. <a href=\"https://doi.org/10.1371/journal.pone.0012189\">doi:10.1371/journal.pone.0012189</a>",
    "Moskwik M. 2014. Recent elevational range expansions in plethodontid salamanders (Amphibia: Plethodontidae) in the southern Appalachian Mountains. <i>Journal of Biogeography</i> 41:1957–1966. <a href=\"https://doi.org/10.1111/jbi.12352\">doi:10.1111/jbi.12352</a>",
    "Nicholson KE (ed.). 2025. <i>Scientific and Standard English Names of Amphibians and Reptiles of North America North of Mexico</i>, 9th ed. SSAR Herpetological Circular.",
    "NC Natural Heritage Program. 2024. <i>Natural Heritage Program List of Rare Animal Species of North Carolina</i>. <a href=\"https://www.ncnhp.org/media/816/open\">ncnhp.org</a>",
    "NC Wildlife Resources Commission. 15A NCAC 10I .0103–.0105, Endangered, Threatened and Special Concern species (as amended 1 Oct 2024; 2026 amendment proposed). <a href=\"https://www.ncwildlife.gov/hunting/regulations/proposed-regulations/endangered-threatened-and-special-concern-species-rule-changes-and-public-comments\">ncwildlife.gov</a>",
    "NC Wildlife Resources Commission. 2025. <i>North Carolina Wildlife Action Plan</i>. <a href=\"https://www.ncwildlife.gov/state-wildlife-action-plan\">ncwildlife.gov</a>",
    "Olander L et al. 2026. Final report on eastern hellbender habitat after Hurricane Helene, Southeast Climate Adaptation Science Center (9 Jul 2026). <a href=\"https://secasc.ncsu.edu/wp-content/uploads/sites/178/2026/07/2026.07.09_Olander_Hellbender_Final_Report_508compliant.pdf\">secasc.ncsu.edu</a>",
    "Patton A, Apodaca JJ, Corser JD, Wilson CR, Williams LA, Cameron AD, Wake DB. 2019. A new green salamander in the southern Appalachians: evolutionary history of <i>Aneides aeneus</i> and implications for management and conservation with the description of a cryptic microendemic species. <i>Copeia</i> 107:748–763. <a href=\"https://doi.org/10.1643/CH-18-052\">doi:10.1643/CH-18-052</a>",
    "Petranka JW. 1998. <i>Salamanders of the United States and Canada</i>. Smithsonian Institution Press.",
    "Pitt AL, Shinskie JL, Tavano JJ, Hartzell SM, Delahunty T, Spear SF. 2017. Decline of a giant salamander assessed with historical records, environmental DNA and multi-scale habitat data. <i>Freshwater Biology</i> 62:967–976. <a href=\"https://doi.org/10.1111/fwb.12917\">doi:10.1111/fwb.12917</a>",
    "Pugh MW, Hutchins M, Madritch M, Siefferman L, Gangloff MM. 2016. Land-use and local physical and chemical habitat parameters predict site occupancy by hellbender salamanders. <i>Hydrobiologia</i> 770:105–116. <a href=\"https://doi.org/10.1007/s10750-015-2570-0\">doi:10.1007/s10750-015-2570-0</a>",
    "Pyron RA, Beamer DA. 2022. <i>Zootaxa</i> 5134:151–196. <a href=\"https://doi.org/10.11646/zootaxa.5134.2.1\">doi:10.11646/zootaxa.5134.2.1</a>",
    "Pyron RA, Beamer DA. 2022. Nomenclatural solutions for diagnosing &lsquo;cryptic&rsquo; species using molecular and morphological data facilitate a taxonomic revision of the black-bellied salamanders. <i>Bionomina</i> 27:1–43. <a href=\"https://doi.org/10.11646/bionomina.27.1.1\">doi:10.11646/bionomina.27.1.1</a>",
    "Pyron RA, Beamer DA. 2022. A systematic revision of the Ocoee salamander, <i>Desmognathus ocoee</i>, with description of two new species from the southern Blue Ridge Mountains. <i>Zootaxa</i> 5190:207–240. <a href=\"https://doi.org/10.11646/zootaxa.5190.2.3\">doi:10.11646/zootaxa.5190.2.3</a>",
    "Pyron RA, Beamer DA. 2023. <i>Zootaxa</i> 5270:262–280. <a href=\"https://doi.org/10.11646/zootaxa.5270.2.5\">doi:10.11646/zootaxa.5270.2.5</a>",
    "Pyron RA, Beamer DA. 2023. <i>Zootaxa</i> 5311:451–504. <a href=\"https://doi.org/10.11646/zootaxa.5311.4.1\">doi:10.11646/zootaxa.5311.4.1</a>",
    "Pyron RA, O'Connell KA, Duncan SC, Burbrink FT, Beamer DA. 2023. Speciation hypotheses from phylogeographic delimitation yield an integrative taxonomy for seal salamanders (<i>Desmognathus monticola</i>). <i>Systematic Biology</i> 72:179–197. <a href=\"https://doi.org/10.1093/sysbio/syac065\">doi:10.1093/sysbio/syac065</a>",
    "Richgels KLD, Russell RE, Adams MJ, White CL, Grant EHC. 2016. Spatial variation in risk and consequence of <i>Batrachochytrium salamandrivorans</i> introduction in the USA. <i>Royal Society Open Science</i> 3:150616. <a href=\"https://doi.org/10.1098/rsos.150616\">doi:10.1098/rsos.150616</a>",
    "Shaw, Chastain &amp; Fitzpatrick. 2025. <i>PeerJ</i> 13:e20110. <a href=\"https://doi.org/10.7717/peerj.20110\">doi:10.7717/peerj.20110</a>",
    "Souza MJ, Gray MJ, Colclough P, Miller DL. 2012. Prevalence of infection by <i>Batrachochytrium dendrobatidis</i> and ranavirus in eastern hellbenders in eastern Tennessee. <i>Journal of Wildlife Diseases</i> 48:560–566. <a href=\"https://doi.org/10.7589/0090-3558-48.3.560\">doi:10.7589/0090-3558-48.3.560</a>",
    "Spear SF, Groves JD, Williams LA, Waits LP. 2015. Using environmental DNA methods to improve detectability in a hellbender monitoring program. <i>Biological Conservation</i> 183:38–45. <a href=\"https://doi.org/10.1016/j.biocon.2014.11.016\">doi:10.1016/j.biocon.2014.11.016</a>",
    "Tilley SG et al. 2013. <i>Ecology and Evolution</i> 3:2547–2567. <a href=\"https://doi.org/10.1002/ece3.636\">doi:10.1002/ece3.636</a>",
    "Unger SD et al. 2017. <i>Southeastern Naturalist</i> 16:N9–N13. <a href=\"https://doi.org/10.1656/058.016.0212\">doi:10.1656/058.016.0212</a>",
    "Unger SD et al. 2020. <i>Southeastern Naturalist</i> 19:742–758. <a href=\"https://doi.org/10.1656/058.019.0411\">doi:10.1656/058.019.0411</a>",
    "US Fish and Wildlife Service. 2019. 12-month finding for the eastern hellbender and endangered status for the Missouri DPS. 84 FR 13223.",
    "US Fish and Wildlife Service. 2021. Endangered status for the Missouri distinct population segment of eastern hellbender. 86 FR 13465. <a href=\"https://www.govinfo.gov/content/pkg/FR-2021-03-09/html/2021-04629.htm\">govinfo.gov</a>",
    "US Fish and Wildlife Service. 2024. 90-day findings, including the Hickory Nut Gorge green salamander. 89 FR 4884. <a href=\"https://www.govinfo.gov/content/pkg/FR-2024-01-25/html/2024-01454.htm\">govinfo.gov</a>",
    "US Fish and Wildlife Service. 2024. Endangered species status for the eastern hellbender (proposed rule). 89 FR 100934. <a href=\"https://www.govinfo.gov/content/pkg/FR-2024-12-13/html/2024-28352.htm\">govinfo.gov</a>",
    "US Fish and Wildlife Service. 2025. Injurious wildlife listing of salamanders due to risk of <i>Bsal</i>. 90 FR 2170. <a href=\"https://www.govinfo.gov/content/pkg/FR-2025-01-10/html/2024-31203.htm\">govinfo.gov</a>",
    "Waddle JH et al. 2020. <i>Batrachochytrium salamandrivorans</i> (Bsal) not detected in an intensive survey of wild North American amphibians. <i>Scientific Reports</i> 10:13012. <a href=\"https://doi.org/10.1038/s41598-020-69486-x\">doi:10.1038/s41598-020-69486-x</a>",
    "Walls SC. 2009. The role of climate in the dynamics of a hybrid zone in Appalachian salamanders. <i>Global Change Biology</i> 15:1903–1910. <a href=\"https://doi.org/10.1111/j.1365-2486.2009.01867.x\">doi:10.1111/j.1365-2486.2009.01867.x</a>"
  ];

  return { families, habitats, basins, ranges, zones, refPeaks, species, refs };
})();
