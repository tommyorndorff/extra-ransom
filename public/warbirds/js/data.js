/* Aircraft data. Figures are typical published values for the listed sub-variant;
   real numbers vary by altitude, load, fuel grade and source. */
window.AIRCRAFT = [
  {
    id: "p51d",
    name: "P-51D Mustang",
    maker: "North American Aviation",
    nation: "United States",
    nationKey: "us",
    role: "Long-range escort fighter",
    roleKey: "fighter",
    service: [1942, 1945],
    firstFlight: "26 Oct 1940",
    built: "~15,500 (all Mustangs)",
    crew: 1,
    engine: "Packard V-1650-7 Merlin, 1,490 hp (1,720 hp war emergency)",
    photos: [
      { key: "p51d-361", caption: "P-51D of the 374th Fighter Squadron, 361st Fighter Group" },
      { key: "p51d-cockpit", caption: "Restored P-51D cockpit: K-14 gunsight above the panel" },
      { key: "p51d-italy", caption: "“American Beauty”, 31st Fighter Group, over Italy in 1944" }
    ],
    specs: { speed: 437, range: 1650, ceiling: 41900, climb: 3200, power: 1490, weight: 12100, guns: 6 },
    armament: "6 × .50 cal M2 Browning, 1,880 rounds; up to 2,000 lb of bombs or 10 rockets",
    interior: "You sit low behind a deep armored seat, the bubble canopy giving a clear 360° view that earlier fighters never had. The K-14 gyro gunsight sits above the panel and works out lead for you as you track a target. Throttle, propeller and mixture levers sit on the left wall; the fuel selector is on the floor between your feet. Behind the seat is an 85-gallon fuselage tank that you burn first, because when it is full it pushes the centre of gravity so far aft that hard maneuvering is dangerous.",
    strengths: [
      "Range: with two drop tanks it could fly from England to Berlin, fight, and fly home.",
      "The two-stage, two-speed supercharger kept full power above 25,000 ft, where the bombers flew.",
      "A laminar-flow wing and a radiator duct that recovered thrust from waste heat made it unusually clean and fast.",
      "The bubble canopy and K-14 gunsight let average pilots see more and hit more."
    ],
    weaknesses: [
      "A liquid-cooled engine: one bullet through the radiator or coolant lines and you had minutes left.",
      "Six .50 cal guns were light against heavily built German bombers.",
      "Tricky handling with the fuselage tank full."
    ],
    fact: "USAAF Mustang pilots were credited with 4,950 enemy aircraft destroyed in Europe, more than any other American fighter."
  },
  {
    id: "spitfire",
    name: "Spitfire Mk IX",
    maker: "Supermarine",
    nation: "United Kingdom",
    nationKey: "uk",
    role: "Air superiority fighter",
    roleKey: "fighter",
    service: [1938, 1945],
    firstFlight: "5 Mar 1936",
    built: "~20,300 (all Spitfires)",
    crew: 1,
    engine: "Rolls-Royce Merlin 61/66, 1,565–1,720 hp",
    photos: [
      { key: "spitfire", caption: "Spitfire Mk IX flying past" },
      { key: "spitfire-cockpit", caption: "Spitfire cockpit: spade-grip stick and the blind-flying panel" }
    ],
    specs: { speed: 408, range: 434, ceiling: 43000, climb: 4100, power: 1565, weight: 7500, guns: 4 },
    armament: "2 × 20 mm Hispano cannon and 4 × .303 Browning (or 2 × .50 cal on the E wing)",
    interior: "The cockpit is famously tight: your shoulders nearly touch both sides. A spade-grip control column fires the guns with a brass button, and the center “blind-flying panel” groups the six instruments needed to fly in cloud. A small door on the left side folds down so you can climb in. The narrow-track undercarriage is raised by a hand pump on early marks, so you can spot a new pilot by the way the nose bobs on climb-out.",
    strengths: [
      "The thin elliptical wing gave a very tight turn and gentle, predictable stall warning.",
      "The Mk IX’s two-stage Merlin answered the Fw 190 almost overnight in 1942.",
      "A long development life: from 1,030 hp in 1938 to over 2,000 hp by 1945."
    ],
    weaknesses: [
      "Short legs: never designed for long escort missions.",
      "Early Merlins with carburettors cut out under negative g, a problem fixed by a simple fuel restrictor.",
      "The narrow undercarriage made ground handling unforgiving."
    ],
    fact: "The Spitfire was the only British fighter in continuous production from before the war to after it."
  },
  {
    id: "bf109",
    name: "Bf 109 G-6",
    maker: "Messerschmitt",
    nation: "Germany",
    nationKey: "de",
    role: "Interceptor and fighter",
    roleKey: "fighter",
    service: [1937, 1945],
    firstFlight: "29 May 1935",
    built: "~34,000 (all variants)",
    crew: 1,
    engine: "Daimler-Benz DB 605A, 1,475 hp",
    photos: [
      { key: "bf109-pilot", caption: "A Bf 109 G-6 pilot under the heavily framed canopy" },
      { key: "bf109-cockpit", caption: "Looking down into a Bf 109 cockpit, canopy hinged open to the right" }
    ],
    specs: { speed: 386, range: 530, ceiling: 39370, climb: 3345, power: 1475, weight: 7496, guns: 3 },
    armament: "1 × 20 mm MG 151/20 (or 30 mm MK 108) through the propeller hub, 2 × 13 mm MG 131",
    interior: "The cockpit is cramped and you sit with your legs nearly straight out. The heavy canopy hinges to the right and cannot be opened in flight, so the view to the rear is poor. Fuel injection meant the engine kept running through negative-g pushovers that would choke a carburettor. The propeller pitch was set with a thumb switch on the throttle and read on a clock-style gauge.",
    strengths: [
      "Direct fuel injection allowed abrupt pushovers into a dive that pursuers could not follow.",
      "A cannon firing through the propeller hub concentrated firepower on the centreline.",
      "Simple to build and kept in production throughout the war."
    ],
    weaknesses: [
      "A narrow, splayed undercarriage caused a large number of takeoff and landing accidents.",
      "Controls grew very heavy at high speed.",
      "Short range limited it over Britain in 1940."
    ],
    fact: "The Bf 109 is the most-produced fighter aircraft in history."
  },
  {
    id: "fw190",
    name: "Fw 190 A-8",
    maker: "Focke-Wulf",
    nation: "Germany",
    nationKey: "de",
    role: "Fighter and bomber destroyer",
    roleKey: "fighter",
    service: [1941, 1945],
    firstFlight: "1 Jun 1939",
    built: "~20,000",
    crew: 1,
    engine: "BMW 801 D-2 radial, 1,700 hp (about 2,000 hp with boost)",
    photos: [
      { key: "fw190", caption: "Captured Fw 190 being test-flown by the Allies, April 1944" },
      { key: "fw190-2", caption: "The same captured Fw 190 near NAS Patuxent River, 1944" }
    ],
    specs: { speed: 408, range: 500, ceiling: 37430, climb: 3000, power: 1700, weight: 9735, guns: 6 },
    armament: "4 × 20 mm MG 151/20 cannon, 2 × 13 mm MG 131",
    interior: "The cockpit was designed around the pilot: a reclined seat, a clear sliding canopy, and electric switches in place of hand cranks. The Kommandogerät, a mechanical “brain”, set propeller pitch, mixture, boost and magneto timing from the throttle alone, so the pilot moved one lever instead of four.",
    strengths: [
      "When it appeared in 1941 it outclassed the Spitfire Mk V in almost every respect.",
      "A very fast roll rate and light ailerons.",
      "A wide undercarriage and tough radial engine made it practical from rough forward airfields."
    ],
    weaknesses: [
      "The BMW 801 lost power above about 20,000 ft, the height of Allied bomber streams.",
      "Its sharp high-speed stall could flick it into a spin without warning."
    ],
    fact: "The RAF got a perfect example in June 1942 when a lost German pilot landed at RAF Pembrey in Wales by mistake."
  },
  {
    id: "zero",
    name: "A6M2 Zero",
    maker: "Mitsubishi",
    nation: "Japan",
    nationKey: "jp",
    role: "Carrier fighter",
    roleKey: "naval",
    service: [1940, 1945],
    firstFlight: "1 Apr 1939",
    built: "10,939",
    crew: 1,
    engine: "Nakajima Sakae 12 radial, 940 hp",
    photos: [
      { key: "zero", caption: "Flying A6M Zero at Planes of Fame, 2009" },
      { key: "zero-cockpit", caption: "Zero cockpit, built light and spare" }
    ],
    specs: { speed: 331, range: 1929, ceiling: 33000, climb: 3100, power: 940, weight: 6164, guns: 4 },
    armament: "2 × 20 mm Type 99 cannon, 2 × 7.7 mm Type 97 machine guns",
    interior: "Everything in the Zero was built to save weight, down to the lightening holes punched through the cockpit structure. There is no armor plate behind the seat and the fuel tanks did not seal themselves, which bought range and agility at the cost of the pilot’s protection. Instruments are simple and well grouped, and the canopy gives good all-round view.",
    strengths: [
      "Astonishing range: patrols of over 1,900 miles let it appear far from any expected base.",
      "At low speed it out-turned every Allied fighter it met in 1941–42.",
      "Light controls and gentle handling at carrier approach speeds."
    ],
    weaknesses: [
      "No armor or self-sealing tanks: short bursts set it on fire.",
      "Ailerons stiffened badly above about 300 mph, so it could not roll with faster opponents.",
      "The 940 hp engine gave little margin for later upgrades."
    ],
    fact: "A nearly intact Zero that crashed on Akutan Island in 1942 let US engineers test-fly it and develop tactics against it."
  },
  {
    id: "p47",
    name: "P-47D Thunderbolt",
    maker: "Republic Aviation",
    nation: "United States",
    nationKey: "us",
    role: "Fighter-bomber",
    roleKey: "fighter",
    service: [1942, 1945],
    firstFlight: "6 May 1941",
    built: "15,636",
    crew: 1,
    engine: "Pratt & Whitney R-2800-59 Double Wasp, 2,000 hp (2,300 hp war emergency)",
    photos: [
      { key: "p47", caption: "P-47D-25 Thunderbolt in flight with the bubble canopy" },
      { key: "p47-museum", caption: "P-47 in invasion stripes at the Museum of Flight, Seattle" }
    ],
    specs: { speed: 433, range: 800, ceiling: 43000, climb: 3120, power: 2000, weight: 17500, guns: 8 },
    armament: "8 × .50 cal M2 Browning; up to 2,500 lb of bombs or 10 × 5-inch rockets",
    interior: "The “Jug” had the roomiest single-seat cockpit of the war. Pilots joked you could dodge enemy fire by running around inside it. A turbosupercharger in the rear fuselage, fed by ducts running under the cockpit floor, gave full power at 30,000 ft. Heavy armor and a big radial engine in front put a lot of metal between the pilot and the enemy.",
    strengths: [
      "Extraordinarily rugged: pilots regularly brought them home with cylinders shot away.",
      "Eight .50 cal guns and a big bomb load made it the best Allied ground-attack fighter.",
      "Unmatched diving speed."
    ],
    weaknesses: [
      "Heavy and thirsty: early models could not reach deep into Germany.",
      "A slow climb compared with lighter fighters."
    ],
    fact: "The P-47 is the most-produced American fighter of all time."
  },
  {
    id: "f4u",
    name: "F4U-1D Corsair",
    maker: "Vought",
    nation: "United States",
    nationKey: "us",
    role: "Carrier fighter-bomber",
    roleKey: "naval",
    service: [1942, 1945],
    firstFlight: "29 May 1940",
    built: "12,571",
    crew: 1,
    engine: "Pratt & Whitney R-2800-8W Double Wasp, 2,250 hp with water injection",
    photos: [
      { key: "f4u", caption: "F4U-1A Corsairs of VF-17, the “Jolly Rogers”, March 1944" },
      { key: "f4u-cockpit", caption: "Corsair cockpit, set far back behind the long nose" }
    ],
    specs: { speed: 425, range: 1015, ceiling: 36900, climb: 3180, power: 2000, weight: 14000, guns: 6 },
    armament: "6 × .50 cal M2 Browning; up to 2,000 lb of bombs or 8 rockets",
    interior: "The cockpit sits far aft behind a 14-foot nose, so on a carrier approach the pilot could see almost nothing ahead. Pilots flew a curving approach to keep the deck in view until the last moment. Later models raised the seat and fitted a clearer canopy. The inverted gull wing let the main gear stay short and strong while clearing a 13-foot propeller.",
    strengths: [
      "The first US single-engine fighter to exceed 400 mph in level flight.",
      "Equally capable as a fighter and as a bomb and rocket carrier.",
      "A credited kill ratio of about 11 to 1 against Japanese aircraft."
    ],
    weaknesses: [
      "Early versions bounced on landing and stalled one wing first, delaying carrier service until 1944.",
      "Poor forward view over the long nose on takeoff and landing."
    ],
    fact: "Japanese troops on Okinawa reportedly called it “whistling death” for the sound of air through its wing-root oil coolers."
  },
  {
    id: "p38",
    name: "P-38J Lightning",
    maker: "Lockheed",
    nation: "United States",
    nationKey: "us",
    role: "Twin-engine heavy fighter",
    roleKey: "heavy",
    service: [1941, 1945],
    firstFlight: "27 Jan 1939",
    built: "10,037",
    crew: 1,
    engine: "2 × Allison V-1710 turbosupercharged, 1,425 hp each",
    photos: [
      { key: "p38", caption: "P-38J Lightning over California, around 1944" },
      { key: "p38-cockpit", caption: "P-38 cockpit, with a control wheel instead of a stick" }
    ],
    specs: { speed: 414, range: 1300, ceiling: 44000, climb: 4750, power: 2850, weight: 21600, guns: 5 },
    armament: "1 × 20 mm Hispano cannon and 4 × .50 cal guns grouped in the nose",
    interior: "The pilot sits in a central nacelle between the twin booms, using a control wheel rather than a stick. With two engines there are two of everything: two sets of throttles, propeller levers and engine gauges. All the guns are in the nose right in front of you, so there is no convergence to set and the stream of fire is a straight line. Early models were cold at altitude because the heater was weak.",
    strengths: [
      "Concentrated nose armament was deadly at any range.",
      "Two engines brought many pilots home on one over the Pacific.",
      "Turbosuperchargers gave strong performance at high altitude."
    ],
    weaknesses: [
      "Complex to fly and maintain, and expensive to build.",
      "Compressibility in steep dives could lock the controls until later dive flaps were added.",
      "Its distinctive outline was easy for enemy pilots to spot."
    ],
    fact: "Lightnings flew the 1943 mission that shot down Admiral Yamamoto, more than 400 miles each way."
  },
  {
    id: "hurricane",
    name: "Hurricane Mk I",
    maker: "Hawker",
    nation: "United Kingdom",
    nationKey: "uk",
    role: "Interceptor",
    roleKey: "fighter",
    service: [1937, 1945],
    firstFlight: "6 Nov 1935",
    built: "~14,500",
    crew: 1,
    engine: "Rolls-Royce Merlin III, 1,030 hp",
    photos: [
      { key: "hurricane", caption: "Hurricane Mk I over Egypt, October 1940" },
      { key: "hurricane-2", caption: "Hurricane Mk IIc PZ865, the last Hurricane built, flying with the Battle of Britain Memorial Flight" }
    ],
    specs: { speed: 340, range: 600, ceiling: 36000, climb: 2780, power: 1030, weight: 6600, guns: 8 },
    armament: "8 × .303 Browning machine guns",
    interior: "The Hurricane’s cockpit sits high, with a good view over the nose and a roomy feel compared with the Spitfire. Behind the pilot the fuselage is steel tube, wooden formers and doped fabric, the same way Hawker built biplanes. Ground crews could patch bullet holes with fabric and dope in minutes, and cannon shells often passed straight through without exploding.",
    strengths: [
      "Easy to build, fly and repair: just what the RAF needed in 1940.",
      "A stable gun platform with eight guns grouped close together.",
      "A wide undercarriage suited rough grass fields."
    ],
    weaknesses: [
      "Slower than the Bf 109 E, especially at altitude.",
      "The fabric-covered fuselage burned easily."
    ],
    fact: "Hurricanes were credited with about 60% of the RAF’s victories in the Battle of Britain."
  },
  {
    id: "b17",
    name: "B-17G Flying Fortress",
    maker: "Boeing",
    nation: "United States",
    nationKey: "us",
    role: "Heavy bomber",
    roleKey: "bomber",
    service: [1938, 1945],
    firstFlight: "28 Jul 1935",
    built: "12,731",
    crew: 10,
    engine: "4 × Wright R-1820-97 Cyclone turbosupercharged, 1,200 hp each",
    photos: [
      { key: "b17", caption: "B-17Gs of the 490th Bombardment Group on a mission" },
      { key: "b17-cockpit", caption: "Pilot and co-pilot stations" },
      { key: "b17-waist", caption: "Waist gun positions looking aft toward the tail" }
    ],
    specs: { speed: 287, range: 2000, ceiling: 35600, climb: 900, power: 4800, weight: 65500, guns: 13 },
    armament: "13 × .50 cal M2 Browning; typically 4,000–6,000 lb of bombs on long missions",
    interior: "Ten men worked in an unpressurized, unheated aluminum tube at –50°F. The bombardier sat in the Plexiglas nose with the Norden bombsight and the chin turret. Behind the pilots, the top-turret gunner doubled as flight engineer. A narrow catwalk crossed the bomb bay to the radio room, then the cramped ball turret, two waist gunners standing at open windows, and the tail gunner kneeling alone at the very back. Crews wore electrically heated suits and oxygen masks for missions that lasted eight hours or more.",
    strengths: [
      "Famously tough: B-17s returned with whole sections of tail or wing shot away.",
      "Thirteen heavy machine guns for formation defense.",
      "Stable and forgiving to fly in tight formation for hours."
    ],
    weaknesses: [
      "A small bomb load for its size compared with British heavies.",
      "Unescorted daylight raids in 1943 suffered terrible losses until the long-range fighters arrived."
    ],
    fact: "A B-17 crew had to fly 25 missions to complete a tour in 1943. Many did not make it, which is why the Memphis Belle’s completion was celebrated."
  }
];

/* Mustang development story. */
window.MUSTANG_VARIANTS = [
  {
    id: "na73x", label: "NA-73X", year: 1940,
    title: "A fighter on a deadline",
    text: "Britain wanted North American Aviation to build Curtiss P-40s under licence. NAA offered to design something better instead. The prototype airframe was rolled out 102 days after the order was signed, and first flew on 26 October 1940.",
    stats: { engine: "Allison V-1710", speed: "~382 mph", guns: "4 .50 cal + 4 .30 cal (planned)", canopy: "Framed" },
    photo: null
  },
  {
    id: "p51a", label: "Mustang I / P-51A", year: 1942,
    title: "Fast low, breathless high",
    text: "With a single-stage Allison engine, the first Mustangs were the fastest fighters in the RAF below 15,000 ft, but power fell away higher up. The RAF used them for low-level reconnaissance and ground attack, and the USAAF built a dive-bomber version, the A-36 Apache.",
    stats: { engine: "Allison V-1710-81", speed: "390 mph", guns: "4 .50 cal", canopy: "Framed" },
    photo: null
  },
  {
    id: "p51b", label: "P-51B / C", year: 1943,
    title: "The Merlin transplant",
    text: "Rolls-Royce test pilot Ronnie Harker suggested fitting a two-stage Merlin. The result was transformative: about 440 mph at 30,000 ft and enough range to escort bombers deep into Germany. P-51Bs flew their first long-range escort missions in December 1943.",
    stats: { engine: "Packard V-1650-3", speed: "440 mph", guns: "4 .50 cal", canopy: "Framed, later Malcolm hood" },
    photo: "p51b"
  },
  {
    id: "p51d", label: "P-51D", year: 1944,
    title: "The definitive Mustang",
    text: "A cut-down rear fuselage and a teardrop bubble canopy gave the pilot all-round vision. Six guns replaced four, with ammunition feeds that no longer jammed in hard turns, and the K-14 gyro gunsight worked out lead automatically. About 8,000 D-models were built, more than any other version.",
    stats: { engine: "Packard V-1650-7", speed: "437 mph", guns: "6 .50 cal", canopy: "Bubble" },
    photo: "p51d-31fg"
  },
  {
    id: "redtails", label: "Red Tails", year: 1944,
    title: "The 332nd Fighter Group",
    text: "The Tuskegee Airmen, the first Black military aviators in the US armed forces, flew P-51s from Italy with tails painted bright red. Escorting Fifteenth Air Force bombers to targets including Berlin, they earned a reputation for staying with the bombers rather than chasing personal victories.",
    stats: { engine: "Packard V-1650-7", speed: "437 mph", guns: "6 .50 cal", canopy: "Bubble" },
    photo: "p51-redtail"
  },
  {
    id: "p51h", label: "P-51H", year: 1945,
    title: "Lighter, faster, too late",
    text: "A near-total redesign using lighter structure and a more powerful Merlin made the P-51H the fastest Mustang, at about 472 mph. It reached units just as the war ended and never saw combat.",
    stats: { engine: "Packard V-1650-9", speed: "472 mph", guns: "6 .50 cal", canopy: "Bubble" },
    photo: null
  }
];

/* Hotspots on the P-51D side photo (percent of image box). Tuned after viewing the image. */
window.MUSTANG_HOTSPOTS = [
  { id: "prop", x: 21.6, y: 56.5, label: "Propeller", title: "Four-blade Hamilton Standard propeller",
    text: "An 11 ft 2 in constant-speed propeller. A governor changes the blade angle automatically so the engine holds the RPM the pilot selects, whether climbing slowly or diving fast.",
    figure: "11 ft 2 in", figureNote: "propeller diameter" },
  { id: "engine", x: 30.5, y: 54.5, label: "Merlin engine", title: "Packard-built Rolls-Royce Merlin",
    text: "A 27-litre liquid-cooled V12, built under licence by Packard in Detroit. Its two-stage, two-speed supercharger compressed thin high-altitude air twice before it reached the cylinders, so the engine still made full power at 25,000 ft.",
    figure: "1,490 hp", figureNote: "takeoff power; 1,720 hp in war emergency" },
  { id: "guns", x: 39.5, y: 58.5, label: "Guns", title: "Six .50 caliber machine guns",
    text: "Three Browning M2 guns in each wing, set to converge about 300 yards ahead. The P-51D mounted them upright, which cured the jamming in hard turns that plagued the four-gun P-51B.",
    figure: "1,880", figureNote: "rounds carried, about 27 seconds of fire" },
  { id: "tank", x: 44.5, y: 65.5, label: "Drop tank", title: "Drop tanks",
    text: "Two external tanks of 75 or 108 gallons hung under the wings. Pilots flew out on drop-tank fuel and released the tanks when they met enemy fighters, keeping internal fuel for the fight and the flight home.",
    figure: "1,650 mi", figureNote: "range with two 108-gallon tanks" },
  { id: "canopy", x: 46.8, y: 48.4, label: "Bubble canopy", title: "Teardrop canopy",
    text: "The D-model's blown Plexiglas canopy gave a clear view in every direction. Most fighter pilots were shot down by aircraft they never saw, so being able to look behind you mattered as much as speed.",
    figure: "360\u00b0", figureNote: "all-round view" },
  { id: "wing", x: 51, y: 57.6, label: "Laminar wing", title: "Laminar-flow wing",
    text: "NAA shaped the wing with its thickest point further back than usual, keeping the airflow smooth over more of the surface. Combined with careful, flush-riveted construction it cut drag noticeably at cruise speeds.",
    figure: "437 mph", figureNote: "top speed at 25,000 ft" },
  { id: "fueltank", x: 55.5, y: 51.5, label: "Fuselage tank", title: "85-gallon fuselage tank",
    text: "Added behind the pilot to stretch range for Berlin missions. Full, it moved the center of gravity so far back that the aircraft could tighten into a turn by itself, so pilots burned it first.",
    figure: "269 gal", figureNote: "internal fuel, wings plus fuselage" },
  { id: "radiator", x: 58.2, y: 64.2, label: "Radiator scoop", title: "Radiator scoop and the Meredith effect",
    text: "The belly scoop slows incoming air, warms it through the coolant and oil radiators, then squeezes it out of a narrowing exit. The heated, expanding air leaves faster than it entered and gives back a little thrust, cancelling much of the radiator's drag.",
    figure: "Low drag", figureNote: "the scoop recovers some of its own drag as thrust" },
  { id: "tail", x: 77.5, y: 45.5, label: "Tail fin", title: "Dorsal fin fillet",
    text: "Cutting down the rear fuselage for the bubble canopy reduced directional stability, so later P-51Ds gained a small fin extension ahead of the tail. The tail also carried unit codes, like this aircraft's B7 and serial 413704.",
    figure: "44-13704", figureNote: "this aircraft's serial number" }
];

/* Approximate escort radius from East Anglia, in miles, with external tanks. */
window.ESCORT = {
  targets: [
    { name: "Paris", mi: 250 },
    { name: "The Ruhr", mi: 330 },
    { name: "Hamburg", mi: 410 },
    { name: "Schweinfurt", mi: 480 },
    { name: "Berlin", mi: 580 },
    { name: "Munich", mi: 620 }
  ],
  fighters: [
    { id: "spitfire", name: "Spitfire Mk IX", internal: 150, tanks: 250 },
    { id: "p47", name: "P-47D Thunderbolt", internal: 230, tanks: 475 },
    { id: "p38", name: "P-38J Lightning", internal: 300, tanks: 520 },
    { id: "p51d", name: "P-51D Mustang", internal: 400, tanks: 750 }
  ]
};
