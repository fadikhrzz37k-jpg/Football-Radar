import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Flux RSS (si un flux ne marche plus, retire-le ou remplace-le)
FEEDS = [
    ("L’Équipe", "https://dwh.lequipe.fr/api/edito/rss?path=/Football/"),
    ("Foot Mercato", "https://www.footmercato.net/flux-rss"),
    ("RMC Sport", "https://rmcsport.bfmtv.com/rss/football/"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/football/rss.xml"),
]
MAX_PAR_SOURCE = 8


def lire_flux(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 HubFoot"})
    with urllib.request.urlopen(req, timeout=20) as r:
        racine = ET.fromstring(r.read())
    articles = []
    # RSS classique
    for item in racine.iter("item"):
        titre = (item.findtext("title") or "").strip()
        lien = (item.findtext("link") or "").strip()
        if titre and lien:
            articles.append((titre, lien))
    # Atom (au cas où)
    if not articles:
        ns = "{http://www.w3.org/2005/Atom}"
        for entree in racine.iter(ns + "entry"):
            titre = (entree.findtext(ns + "title") or "").strip()
            el = entree.find(ns + "link")
            lien = el.get("href") if el is not None else ""
            if titre and lien:
                articles.append((titre, lien))
    return articles[:MAX_PAR_SOURCE]


def construire_page():
    sections = []
    for nom, url in FEEDS:
        try:
            articles = lire_flux(url)
        except Exception as e:
            print("Flux en échec :", nom, e)
            continue
        if not articles:
            continue
        lignes = "".join(
            f'<a class="art" href="{html.escape(l)}" target="_blank" rel="noopener">{html.escape(t)}</a>'
            for t, l in articles
        )
        sections.append(f"<h2>{html.escape(nom)}</h2>{lignes}")
    if not sections:
        sections.append("<p>Aucune actu récupérée pour le moment.</p>")
    maintenant = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")
    return PAGE.replace("{{CONTENU}}", "".join(sections)).replace("{{DATE}}", maintenant)


PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Football Radar – actus foot du jour, transferts et résultats</title>
<meta name="description" content="Football Radar rassemble chaque jour les actus du football : transferts, résultats et analyses, mises à jour automatiquement.">
<meta name="robots" content="index, follow">
<meta property="og:title" content="Football Radar – actus foot du jour">
<meta property="og:description" content="Les actus du football, mises à jour automatiquement toute la journée.">
<meta property="og:type" content="website">
<style>
:root{--bg:#f5f7f5;--card:#fff;--text:#16201a;--muted:#5d6b62;--accent:#15803d;--border:#dde5df}
@media (prefers-color-scheme:dark){:root{--bg:#0e1511;--card:#17211b;--text:#eef4f0;--muted:#9fb0a5;--accent:#4ade80;--border:#26352c}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.45}
main{max-width:640px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:28px;margin:8px 0 4px}
.sub{color:var(--muted);margin:0 0 8px}
h2{font-size:15px;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);margin:24px 0 8px}
a.art{display:block;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px;margin-bottom:8px;color:var(--text);text-decoration:none}
</style>
</head>
<body>
<main>
<h1>⚽ Football Radar</h1>
<p class="sub">Actus mises à jour automatiquement. Dernière mise à jour : {{DATE}}</p>
{{CONTENU}}
</main>
</body>
</html>
"""

if __name__ == "__main__":
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(construire_page())
    print("index.html généré")
