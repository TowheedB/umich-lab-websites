#!/usr/bin/env python3
"""Generate 56 prototype lab sites (two design variants per lab) + a root gallery.

Usage:  python3 build/build.py            -> writes into ./labs/<slug>/{a,b}/ and ./index.html
"""
import csv, json, os, re, shutil, hashlib, math, random, html
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT = ROOT  # repo root is the GitHub Pages root
LABS_DIR = OUT / "labs"

env = Environment(
    loader=FileSystemLoader(str(BUILD / "templates")),
    autoescape=select_autoescape(["html", "j2"]),
    trim_blocks=True, lstrip_blocks=True,
)

# --------------------------------------------------------------------------------------
# Design system: 6 templates x 8 palettes
# --------------------------------------------------------------------------------------
TEMPLATES = ["editorial", "atlas", "monograph", "specimen", "ledger", "horizon"]

PALETTES = {
    # name: (accent, accent-strong, accent-soft(light), accent-soft(dark), tint for hero)
    "indigo":  dict(light="#8b93ff", accent="#4f46e5", strong="#3730a3", soft="#eef0ff", softd="#1e1b4b", ink="#15172b"),
    "teal":    dict(light="#3fcfbf", accent="#0f766e", strong="#115e59", soft="#e6f7f4", softd="#0b2f2c", ink="#0f2a28"),
    "crimson": dict(light="#f87171", accent="#b91c1c", strong="#7f1d1d", soft="#fdecec", softd="#3b0f0f", ink="#2a1313"),
    "forest":  dict(light="#7fd38f", accent="#2f6b3a", strong="#1f4a28", soft="#e9f4ea", softd="#102416", ink="#122017"),
    "amber":   dict(light="#f5b437", accent="#b45309", strong="#78350f", soft="#fdf3e3", softd="#3a2308", ink="#2a1d0e"),
    "plum":    dict(light="#c58bff", accent="#7e22ce", strong="#581c87", soft="#f5ebff", softd="#2b1040", ink="#22132f"),
    "ocean":   dict(light="#4fb8f0", accent="#0369a1", strong="#075985", soft="#e6f3fb", softd="#0b2838", ink="#0f2130"),
    "slate":   dict(light="#9fb0c8", accent="#334155", strong="#1e293b", soft="#eef2f6", softd="#1b2330", ink="#111827"),
}
PALETTE_NAMES = list(PALETTES)

# Motif for the generated hero artwork, keyed by research vocabulary
MOTIFS = [
    ("neuron",   ["neural", "neuro", "synap", "sleep", "brain", "dopamine", "pain", "itch", "olfact", "sensory", "interocept", "lung-brain"]),
    ("plant",    ["plant", "arabidopsis", "root", "cell wall", "cell-wall", "immunity"]),
    ("microbe",  ["bacteri", "microb", "biofilm", "curli", "antimicrobial", "membrane protein"]),
    ("genome",   ["chromatin", "rna", "genome", "chromosome", "gene regulation", "wnt", "evolution", "dna repair", "epigen"]),
    ("cell",     ["lysosome", "protein", "secretory", "motor", "microtubule", "junction", "cytokinesis", "proliferation", "cell-cycle", "cell cycle", "growth", "organization", "imaging", "oxidative"]),
]

def pick_motif(text):
    t = text.lower()
    for name, keys in MOTIFS:
        if any(k in t for k in keys):
            return name
    return "cell"

# --------------------------------------------------------------------------------------
# Generated hero artwork (deterministic per lab + variant)
# --------------------------------------------------------------------------------------
def hero_svg(seed, motif, w=640, h=420):
    rnd = random.Random(seed)
    out = [f'<svg class="hero-art" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Abstract illustration">']
    out.append('<defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">'
               '<stop offset="0" stop-color="var(--accent)" stop-opacity=".95"/>'
               '<stop offset="1" stop-color="var(--accent-strong)" stop-opacity=".8"/></linearGradient>'
               '<radialGradient id="g2"><stop offset="0" stop-color="var(--accent)" stop-opacity=".55"/>'
               '<stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></radialGradient></defs>')
    if motif == "neuron":
        pts = [(rnd.uniform(40, w-40), rnd.uniform(40, h-40)) for _ in range(16)]
        for i, (x, y) in enumerate(pts):
            for j in range(i+1, len(pts)):
                x2, y2 = pts[j]
                d = math.hypot(x-x2, y-y2)
                if d < 190:
                    cx, cy = (x+x2)/2 + rnd.uniform(-40, 40), (y+y2)/2 + rnd.uniform(-40, 40)
                    out.append(f'<path d="M{x:.0f} {y:.0f} Q{cx:.0f} {cy:.0f} {x2:.0f} {y2:.0f}" fill="none" stroke="var(--accent)" stroke-opacity="{max(.12, .6-d/300):.2f}" stroke-width="{1.2 if d>120 else 2}"/>')
        for x, y in pts:
            r = rnd.uniform(5, 16)
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r*2.6:.0f}" fill="url(#g2)"/>')
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="url(#g1)"/>')
    elif motif == "plant":
        def branch(x, y, ang, length, depth):
            if depth == 0 or length < 8: return
            x2 = x + math.cos(ang)*length; y2 = y - math.sin(ang)*length
            out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="var(--accent)" stroke-opacity="{.25+depth*.1:.2f}" stroke-width="{depth*1.1:.1f}" stroke-linecap="round"/>')
            if depth <= 2:
                out.append(f'<ellipse cx="{x2:.0f}" cy="{y2:.0f}" rx="{rnd.uniform(6,12):.0f}" ry="{rnd.uniform(3,6):.0f}" transform="rotate({-math.degrees(ang):.0f} {x2:.0f} {y2:.0f})" fill="url(#g1)" opacity=".85"/>')
            for k in range(rnd.choice([2, 2, 3])):
                branch(x2, y2, ang + rnd.uniform(-.7, .7), length*rnd.uniform(.62, .8), depth-1)
        for bx in (w*.3, w*.55, w*.78):
            branch(bx, h-10, math.pi/2 + rnd.uniform(-.2, .2), rnd.uniform(70, 110), 6)
    elif motif == "microbe":
        for _ in range(26):
            x, y = rnd.uniform(20, w-20), rnd.uniform(20, h-20)
            L, r = rnd.uniform(30, 90), rnd.uniform(8, 16)
            a = rnd.uniform(0, 180)
            out.append(f'<rect x="{x-L/2:.0f}" y="{y-r:.0f}" width="{L:.0f}" height="{2*r:.0f}" rx="{r:.0f}" transform="rotate({a:.0f} {x:.0f} {y:.0f})" fill="url(#g1)" opacity="{rnd.uniform(.35,.95):.2f}"/>')
            out.append(f'<rect x="{x-L/2+6:.0f}" y="{y-r+5:.0f}" width="{L-12:.0f}" height="{2*r-10:.0f}" rx="{r:.0f}" transform="rotate({a:.0f} {x:.0f} {y:.0f})" fill="none" stroke="var(--bg)" stroke-opacity=".5" stroke-width="1.5"/>')
    elif motif == "genome":
        for strand in range(2):
            pts = []
            for i in range(0, w+1, 8):
                y = h/2 + math.sin(i/70 + strand*math.pi) * h*.28
                pts.append(f'{i},{y:.0f}')
            out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="var(--accent)" stroke-opacity=".8" stroke-width="7" stroke-linecap="round"/>')
        for i in range(16, w, 36):
            y1 = h/2 + math.sin(i/70) * h*.28; y2 = h/2 + math.sin(i/70 + math.pi) * h*.28
            out.append(f'<line x1="{i}" y1="{y1:.0f}" x2="{i}" y2="{y2:.0f}" stroke="var(--accent-strong)" stroke-opacity=".45" stroke-width="3"/>')
            out.append(f'<circle cx="{i}" cy="{(y1+y2)/2:.0f}" r="{rnd.uniform(3,7):.0f}" fill="url(#g1)"/>')
    else:  # cell
        for _ in range(14):
            x, y, r = rnd.uniform(40, w-40), rnd.uniform(40, h-40), rnd.uniform(22, 70)
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="var(--accent)" fill-opacity="{rnd.uniform(.08,.22):.2f}" stroke="var(--accent)" stroke-opacity=".6" stroke-width="2"/>')
            out.append(f'<circle cx="{x+rnd.uniform(-r/3,r/3):.0f}" cy="{y+rnd.uniform(-r/3,r/3):.0f}" r="{r*.32:.0f}" fill="url(#g1)"/>')
            for _ in range(rnd.randint(2, 5)):
                out.append(f'<circle cx="{x+rnd.uniform(-r*.7,r*.7):.0f}" cy="{y+rnd.uniform(-r*.7,r*.7):.0f}" r="{rnd.uniform(2,5):.0f}" fill="var(--accent-strong)" opacity=".7"/>')
    out.append('</svg>')
    return "\n".join(out)

# --------------------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------------------
SLUGS = {  # CSV lab name -> research slug
    "Bo Duan Lab": "bo-duan-lab", "C. Duan Lab": "c-duan-lab", "Ming Li Lab": "ming-li-lab",
    "He Lab / Plant-Microbe Interaction": "he-lab", "Dus Laboratory of Molecular Nutrition": "dus-lab",
}

def slugify(lab, last):
    if lab in SLUGS: return SLUGS[lab]
    return re.sub(r"[^a-z0-9]+", "-", last.lower()).strip("-") + "-lab"

def short_lab_name(lab):
    if lab.startswith("He Lab"): return "He Lab"
    if lab.startswith("Dus Lab"): return "Dus Lab"
    return lab

def initials(name):
    parts = [p for p in re.split(r"[\s.]+", name) if p and p[0].isalpha()]
    return "".join(p[0].upper() for p in parts[:2]) or "?"

def load_labs():
    rows = list(csv.DictReader(open(ROOT / "data" / "labs.csv", encoding="utf-8-sig")))
    labs = []
    for r in rows:
        slug = slugify(r["Lab"], r["Last Name"])
        research = json.load(open(ROOT / "research" / f"{slug}.json"))
        themes = [t.strip() for t in r["Suggested Research Themes"].split(";") if t.strip()]
        areas = research["research_areas"] or [{"title": t, "summary": ""} for t in themes]
        pubs = sorted(research["publications"], key=lambda p: -(int(p.get("year") or 0)))
        years = [int(p["year"]) for p in pubs if p.get("year")]
        team = research["team"]
        # group roles for the people page
        order = ["Principal Investigator", "Co-Principal Investigator", "Research Scientist", "Research Investigator", "Postdoctoral", "Graduate", "Lab Manager", "Research Technician", "Technician", "Research Specialist", "Undergraduate", "Visiting", "Other"]
        def bucket(role):
            rl = role.lower()
            for o in order:
                if o.lower().split()[0] in rl: return o
            return "Other"
        groups = {}
        for m in team:
            groups.setdefault(bucket(m["role"]), []).append(dict(m, initials=initials(m["name"])))
        grouped = [(k if k != "Postdoctoral" else "Postdoctoral Researchers", groups[k]) for k in order if k in groups]
        grouped = [(("Graduate Students" if k == "Graduate" else "Undergraduate Researchers" if k == "Undergraduate" else "Lab Members" if k == "Other" else k + ("s" if not k.endswith("s") and k not in ("Postdoctoral Researchers",) else "")), v) for k, v in grouped]
        pi = research["pi"]
        pi["email"] = r["Email"]
        pi["initials"] = initials(pi["name"])
        focus = r["Research Focus"]
        labs.append(dict(
            n=int(r["Priority"]), slug=slug, lab=r["Lab"], short=short_lab_name(r["Lab"]),
            first=r["First Name"], last=r["Last Name"], email=r["Email"],
            focus=focus, keywords=[k.strip() for k in focus.split(";")],
            hero=r["Prototype Hero Line"], themes=themes, existing=r["Existing Lab Website"],
            pi=pi, description=research["lab_description"], areas=areas,
            team_groups=grouped, team_count=len(team), team_flat=[m for _, ms in grouped for m in ms][:5], alumni=research["alumni"],
            pubs=pubs, pub_years=(min(years), max(years)) if years else None,
            news=research["news"][:8], funding=research["funding"], joining=research["joining"],
            address=research["address"], links=research["links"],
            motif=pick_motif(focus + " " + r["Lab"]),
        ))
    return labs

# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------
PAGES = [("index", "Home"), ("research", "Research"), ("publications", "Publications"), ("people", "People"), ("join", "Join us")]

def render_site(lab, variant, template, palette, other_variant):
    outdir = LABS_DIR / lab["slug"] / variant
    outdir.mkdir(parents=True, exist_ok=True)
    pal = PALETTES[palette]
    seed = f"{lab['slug']}-{variant}-{template}"
    art = hero_svg(int(hashlib.md5(seed.encode()).hexdigest(), 16) % 10**8, lab["motif"])
    ctx = dict(lab=lab, variant=variant.upper(), other_variant=other_variant.upper(), template=template,
               palette=pal, palette_name=palette, art=art, pages=PAGES, year=2026)
    for page, label in PAGES:
        cand = f"{template}/{page}.html.j2"
        tpl = env.get_template(cand if (BUILD / "templates" / cand).exists() else f"_pages/{page}.html.j2")
        (outdir / f"{page}.html").write_text(tpl.render(page=page, page_label=label, **ctx))
    css = (BUILD / "templates" / template / "style.css").read_text()
    base_css = (BUILD / "templates" / "_base.css").read_text()
    (outdir / "style.css").write_text(base_css + "\n\n/* ---- template: " + template + " ---- */\n" + css)
    shutil.copy(BUILD / "templates" / "_script.js", outdir / "script.js")
    (outdir / "content.json").write_text(json.dumps({k: lab[k] for k in ("lab", "pi", "description", "areas", "pubs", "team_groups", "news", "joining", "address")}, indent=1, default=str))

def main():
    if LABS_DIR.exists(): shutil.rmtree(LABS_DIR)
    labs = load_labs()
    manifest = []
    for i, lab in enumerate(labs):
        ta, tb = TEMPLATES[i % 6], TEMPLATES[(i + 3) % 6]
        pa, pb = PALETTE_NAMES[i % 8], PALETTE_NAMES[(i + 5) % 8]
        render_site(lab, "a", ta, pa, "b")
        render_site(lab, "b", tb, pb, "a")
        manifest.append(dict(n=lab["n"], slug=lab["slug"], lab=lab["lab"], pi=lab["pi"]["name"], email=lab["email"],
                             focus=lab["focus"], hero=lab["hero"], a=dict(template=ta, palette=pa), b=dict(template=tb, palette=pb),
                             team=lab["team_count"], pubs=len(lab["pubs"]), existing=lab["existing"]))
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    (OUT / "index.html").write_text(env.get_template("_gallery.html.j2").render(labs=manifest, templates=TEMPLATES))
    (OUT / ".nojekyll").write_text("")
    print(f"built {len(labs)*2} sites for {len(labs)} labs")

if __name__ == "__main__":
    main()
