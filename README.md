# U-M MCDB lab website prototypes

Fifty-six prototype lab websites for twenty-eight research groups in the Department of
Molecular, Cellular, and Developmental Biology at the University of Michigan. Each lab
gets two design directions (**A** and **B**) built from the same content, so the PI can
compare and pick a starting point. Every site has five pages (Home, Research,
Publications, People, Join us), light and dark mode, and a responsive layout.

Content was drawn from each lab's current public website and faculty profile: PI bio,
research overview and themes, team roster, 10 recent publications, news items, and
contact details. Anything that could not be sourced is marked as a placeholder.

## Live preview with GitHub Pages

1. Push this repository to GitHub.
2. In the repository, open **Settings → Pages**, set *Source* to **Deploy from a branch**,
   pick the `main` branch and the `/ (root)` folder, and save.
3. After a minute the gallery is at `https://<user>.github.io/<repo>/` and each site at

   ```
   https://<user>.github.io/<repo>/labs/<slug>/a/      (design A)
   https://<user>.github.io/<repo>/labs/<slug>/b/      (design B)
   ```

The `.nojekyll` file is already in place so Pages serves the folders as-is.

## Layout

```
index.html            gallery of all 28 labs with links to both designs
manifest.json         machine-readable index (slug, PI, templates, counts)
labs/<slug>/a|b/      one self-contained static site per design
    index.html research.html publications.html people.html join.html
    style.css script.js content.json
data/labs.csv         lab roster + hero lines + suggested themes
research/<slug>.json  sourced content per lab (edit this to update a site)
build/                generator: build.py + Jinja templates
```

## The six design templates

| Template   | Character                                                              |
|------------|------------------------------------------------------------------------|
| editorial  | Serif display type, two-column hero, numbered theme cards (LS3-style)  |
| atlas      | Dark full-bleed hero with artwork, floating stat bar, sticky blurred nav|
| monograph  | Fixed left sidebar navigation, book-like serif body, ruled lists        |
| specimen   | Centered hero in an organic blob, pill nav, rounded tiles, gradient CTA |
| ledger     | Framed split hero with fact panel, numbered sections, tabular themes    |
| horizon    | Full-width illustrated band, large serif headline, horizontal theme strip |

Templates rotate across labs (A = template *i*, B = template *i+3*) and are combined with
eight accent palettes, so no two neighbouring labs look alike. The hero artwork is a
deterministic SVG generated from the lab's research vocabulary (neurons, cells, plants,
microbes, or genome motifs).

## Rebuilding

```bash
pip install jinja2
python3 build/build.py
```

Edit `research/<slug>.json` to change a lab's content, `build/templates/<template>/` to
change a design, or `TEMPLATES` / `PALETTES` in `build/build.py` to reassign which lab
gets which look. The build is idempotent and regenerates `labs/`, `index.html`, and
`manifest.json`.

## Slugs

akaaboune-lab · aton-lab · buttitta-lab · cadigan-lab · chang-lab · chapman-lab ·
clowney-lab · csankovszki-lab · desantis-lab · bo-duan-lab · c-duan-lab · dus-lab ·
he-lab · jakob-lab · kargbo-hill-lab · kozik-lab · kramer-lab · kumar-lab · ming-li-lab ·
miller-lab · nielsen-lab · schiefelbein-lab · simmons-lab · stockbridge-lab · su-lab ·
vecchiarelli-lab · wierzbicki-lab · wittkopp-lab
