#!/usr/bin/env python3
"""Photo tooling for static/salamanders/.

Finds freely licensed (CC0 / CC BY / CC BY-SA) research-grade iNaturalist photos for
species in js/data.js that have no photo, lets you review them on a contact sheet, then
installs your picks and writes attribution.

    python3 -I tools/salamanders/photos.py fetch   [--all] [--out DIR]   # candidates + contact sheets
    python3 -I tools/salamanders/photos.py install intermedius=0 lycos=1 [--out DIR]
    python3 -I tools/salamanders/photos.py credits                      # regenerate js/credits.js

`fetch` prefers North Carolina observations (iNat place 30) and falls back to range-wide.
Look at every contact sheet before installing: iNat IDs of cryptic Desmognathus are often
locality-based, and the top-voted photo is not always the clearest or even the right taxon.
Requires Pillow. Downloads go to a scratch dir (default: ./.salamander-photos, gitignored).
"""
import argparse, io, json, os, re, shutil, sys, time, urllib.parse, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static", "salamanders")
DATA = os.path.join(ROOT, "js", "data.js")
IMG = os.path.join(ROOT, "assets", "img")
CREDITS_JSON = os.path.join(IMG, "credits.json")
CREDITS_JS = os.path.join(ROOT, "js", "credits.js")
UA = {"User-Agent": "extra-ransom-salamander-page/1.0 (+https://github.com/tommyorndorff/extra-ransom)"}
LIC = {"cc0": ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
       "cc-by": ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
       "cc-by-sa": ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/")}
NC_PLACE = 30


def species_blocks(src):
    """Yield (id, sci, common, block_start, block_end, has_photo) for each species object in data.js."""
    starts = [m.start() for m in re.finditer(r'\{\s*\n\s*id: "', src)]
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else src.index("const refs")
        block = src[s:e]
        sid = re.search(r'id: "([^"]+)"', block).group(1)
        sci = re.search(r'sci: "([^"]+)"', block).group(1)
        common = re.search(r'common: "([^"]+)"', block).group(1)
        yield sid, sci, common, s, e, bool(re.search(r'\bphoto: "', block))


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def search(sci, place):
    q = {"taxon_name": sci, "quality_grade": "research", "photo_license": "cc-by,cc-by-sa,cc0",
         "order_by": "votes", "per_page": 30, "photos": "true"}
    if place:
        q["place_id"] = place
    return json.loads(get("https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(q)))["results"]


def fetch(args):
    from PIL import Image, ImageDraw
    os.makedirs(args.out, exist_ok=True)
    src = open(DATA).read()
    todo = [(sid, sci) for sid, sci, _, _, _, has in species_blocks(src) if args.all or not has]
    cands = {}
    for sid, sci in todo:
        picks = []
        for place in (NC_PLACE, None):
            try:
                res = search(sci, place)
            except Exception as e:  # network hiccup: keep going
                print("search failed", sci, e); res = []
            time.sleep(1.1)  # iNat asks for <= 1 request/second
            for o in res:
                if not (o.get("taxon") or {}).get("name", "").startswith(sci):
                    continue
                p = (o.get("photos") or [None])[0]
                if p and (p.get("license_code") or "").lower() in LIC:
                    picks.append({"obs": o["id"], "photo": p["id"], "url": p["url"].replace("/square.", "/large."),
                                  "license": p["license_code"].lower(), "attribution": p.get("attribution", ""),
                                  "taxon": o["taxon"]["name"], "place": o.get("place_guess") or "", "nc": place == NC_PLACE})
                if len(picks) >= 4:
                    break
            if len(picks) >= 2:
                break
        out = []
        for i, c in enumerate(picks[:4]):
            for attempt in range(3):
                try:
                    im = Image.open(io.BytesIO(get(c["url"]))).convert("RGB")
                    im.thumbnail((1280, 1280))
                    c["file"] = f"{sid}-{i}.jpg"
                    im.save(os.path.join(args.out, c["file"]), quality=80, optimize=True, progressive=True)
                    out.append(c); break
                except Exception as e:
                    print("download retry", sid, i, e); time.sleep(2)
            time.sleep(0.5)
        cands[sid] = out
        print(f"{sid:16s} {sci:32s} {len(out)} candidate(s){' (NC)' if out and out[0]['nc'] else ''}")
    json.dump(cands, open(os.path.join(args.out, "candidates.json"), "w"), indent=1)
    # contact sheets, 9 species per sheet
    ids, W, H = [k for k in cands if cands[k]], 300, 210
    for b in range(0, len(ids), 9):
        chunk = ids[b:b + 9]
        sheet = Image.new("RGB", (4 * W, len(chunk) * (H + 18)), "white"); d = ImageDraw.Draw(sheet)
        for r, sid in enumerate(chunk):
            for i, c in enumerate(cands[sid]):
                t = Image.open(os.path.join(args.out, c["file"])); t.thumbnail((W - 6, H))
                sheet.paste(t, (i * W, r * (H + 18)))
                d.text((i * W + 2, r * (H + 18) + H + 2), f"{sid}={i} {c['license']}{' NC' if c['nc'] else ''}", fill="black")
        sheet.save(os.path.join(args.out, f"sheet{b // 9}.jpg"), quality=82)
    print(f"Review {args.out}/sheet*.jpg, then: photos.py install <id>=<n> ...")


def write_credits_js(cr):
    open(CREDITS_JS, "w").write("/* Generated from assets/img/credits.json by tools/salamanders/photos.py */\n"
                                "window.SAL_CREDITS = " + json.dumps(cr, indent=1, ensure_ascii=False) + ";\n")


def install(args):
    cands = json.load(open(os.path.join(args.out, "candidates.json")))
    src = open(DATA).read()
    info = {sid: (sci, common) for sid, sci, common, *_ in species_blocks(src)}
    cr = json.load(open(CREDITS_JSON))
    states = {"NC": "North Carolina", "TN": "Tennessee", "GA": "Georgia", "SC": "South Carolina", "VA": "Virginia",
              "AL": "Alabama", "WV": "West Virginia", "KY": "Kentucky"}
    for pick in args.picks:
        sid, n = pick.split("="); c = cands[sid][int(n)]; key = "inat-" + sid
        shutil.copy(os.path.join(args.out, c["file"]), os.path.join(IMG, key + ".jpg"))
        m = re.search(r"\(c\)\s*(.*?),\s*(some|no|all) rights", c["attribution"])
        state = "North Carolina" if c["nc"] else next((v for a, v in states.items() if re.search(rf"\b{a}\b|{v}", c["place"])), "")
        common = info[sid][1]
        cr[key] = {"title": f"iNaturalist observation {c['obs']} (photo {c['photo']})",
                   "page": f"https://www.inaturalist.org/observations/{c['obs']}",
                   "artist": (m.group(1) if m else c["attribution"]).strip(),
                   "license": LIC[c["license"]][0], "licenseUrl": LIC[c["license"]][1], "species": c["taxon"],
                   # State only: never put finer locality for sensitive taxa in captions.
                   "caption": f"{common[0].upper() + common[1:]}{', ' + state if state else ''}. iNaturalist research-grade observation."}
        # Set or replace the photo field in this species' block.
        blocks = {b[0]: b for b in species_blocks(src)}
        _, _, _, s, e, has = blocks[sid]
        block = src[s:e]
        block = re.sub(r'photo: "[^"]+"', f'photo: "{key}"', block) if has else block.replace("ranges:", f'photo: "{key}", ranges:', 1) \
            if "ranges:" in block else block.rstrip().rstrip("}").rstrip() + f',\n      photo: "{key}"\n    ' + "}"
        src = src[:s] + block + src[e:]
        print("installed", key)
    open(DATA, "w").write(src)
    json.dump(cr, open(CREDITS_JSON, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    write_credits_js(cr)
    print("Now bump the ?v= query strings in static/salamanders/index.html.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--all", action="store_true", help="also species that already have a photo")
    i = sub.add_parser("install"); i.add_argument("picks", nargs="+", help="species_id=candidate_index")
    sub.add_parser("credits")
    for p in (f, i):
        p.add_argument("--out", default=".salamander-photos")
    args = ap.parse_args()
    if args.cmd == "fetch":
        fetch(args)
    elif args.cmd == "install":
        install(args)
    else:
        write_credits_js(json.load(open(CREDITS_JSON)))


if __name__ == "__main__":
    sys.exit(main())
