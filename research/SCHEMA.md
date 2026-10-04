Write one JSON file per lab at /home/claude/umich-labs/research/<slug>.json with exactly this shape.
Only include facts you actually found on the lab's website (or a PubMed/Google Scholar/UM faculty page). Never invent names, titles, or papers. Leave arrays empty / strings "" when not found.

{
  "slug": "aton-lab",
  "pi": {
    "name": "Sara Aton",
    "title": "e.g. Professor of Molecular, Cellular, and Developmental Biology",
    "bio": "2-4 sentence factual bio in third person drawn from the site (education, career, what the lab studies). Empty string if nothing found.",
    "email": "from CSV",
    "phone": "",
    "office": "building / room if listed",
    "department": "Molecular, Cellular, and Developmental Biology (default unless site says otherwise)",
    "profile_url": "UM faculty profile URL if found"
  },
  "lab_description": "3-6 sentence factual overview of the lab's research, paraphrased from the site. Empty if nothing found.",
  "research_areas": [ {"title": "...", "summary": "1-3 sentences from the site"} ],
  "team": [ {"name": "...", "role": "Postdoctoral Fellow | Graduate Student | Research Technician | Lab Manager | Undergraduate | ...", "note": "optional one-liner"} ],
  "alumni": [ {"name": "...", "role": "...", "now": "optional"} ],
  "publications": [ {"year": 2024, "title": "...", "authors": "...", "venue": "journal", "doi_or_url": ""} ],
  "news": [ {"date": "2024-05", "text": "..."} ],
  "funding": ["NIH", "NSF", ...],
  "joining": "any text about openings / how to join, else empty",
  "address": "street address if listed",
  "links": {"twitter": "", "github": "", "google_scholar": "", "pubmed": "", "other": []},
  "source_notes": "which pages you read and what was missing"
}
