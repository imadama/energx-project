# Master Workflow E — Orchestratie Guide

Hoe je de 5 workflows aan elkaar koppelt tot één geautomatiseerde pipeline.

---

## De 5 Energx workflows

| Workflow | Doel | Inputs | Output |
|---|---|---|---|
| **A** | Tech Audit | domein | technisch rapport (markdown) |
| **B** | Content Audit | URL-lijst of "auto" | content-fixes per URL (markdown) |
| **C** | Keyword Gap | seed-keywords + concurrent-domeinen | gap-rapport met prioriteit (markdown) |
| **D** | Keyword Researcher | seed-thema | kansen-lijst met prio (markdown) |
| **E** | Master Synthese | rapporten A+B+C+D | master-plan + top-10 keywords voor briefs |

Plus de bestaande **Brief Generator** workflow voor de uiteindelijke content-briefs.

---

## Drie integratie-niveaus

### Niveau 1 — Handmatig (start hier)

1. Run Workflow A → kopieer markdown output
2. Run Workflow B → kopieer markdown output
3. Run Workflow C → idem
4. Run Workflow D → idem
5. Plak alle 4 in Workflow E → krijg master-plan
6. Pak top 10 keywords uit master-plan → run Brief Generator handmatig per keyword

**Voordelen:** geen extra setup. Werkt direct na import van DSLs.
**Nadelen:** ~10 min handmatig werk per master-audit. OK voor 1-2× per maand.

### Niveau 2 — Halfautomatisch via Python orchestrator

Externe Python script die Dify's REST API gebruikt om workflows in volgorde te runnen.

```python
# orchestrator.py — minimal scaffolding (uitwerken naar eigen behoefte)
import httpx
import os

DIFY_HOST = "http://100.117.6.53"
APP_KEYS = {
    "tech_audit": os.getenv("DIFY_TECH_AUDIT_KEY"),
    "content_audit": os.getenv("DIFY_CONTENT_AUDIT_KEY"),
    "keyword_gap": os.getenv("DIFY_KEYWORD_GAP_KEY"),
    "keyword_researcher": os.getenv("DIFY_KEYWORD_RESEARCHER_KEY"),
    "master": os.getenv("DIFY_MASTER_KEY"),
    "brief_generator": os.getenv("DIFY_BRIEF_KEY"),
}


def run_workflow(app_name: str, inputs: dict) -> dict:
    """Trigger Dify workflow synchronously and return result."""
    key = APP_KEYS[app_name]
    response = httpx.post(
        f"{DIFY_HOST}/v1/workflows/run",
        headers={"Authorization": f"Bearer {key}"},
        json={"inputs": inputs, "response_mode": "blocking", "user": "orchestrator"},
        timeout=600,
    )
    response.raise_for_status()
    return response.json()


def run_master_audit(domein: str, competitors: list[str], seed_thema: str):
    # Stap 1: parallel runs (in productie: gebruik asyncio of threading)
    tech = run_workflow("tech_audit", {"domein": domein, "max_urls": 20})
    content = run_workflow("content_audit", {"urls_input": "auto", "gsc_site_url": f"sc-domain:{domein.replace('https://', '').replace('http://', '')}"})
    gap = run_workflow("keyword_gap", {
        "seed_keywords": "\n".join(["thuisbatterij kopen", "warmtepomp prijs", "laadpaal installeren"]),
        "competitor_domains": "\n".join(competitors),
        "own_domain": domein,
    })
    researcher = run_workflow("keyword_researcher", {"seed_thema": seed_thema, "regio": ""})

    # Stap 2: feed alles in Master
    master = run_workflow("master", {
        "domein": domein,
        "tech_audit_report": tech["data"]["outputs"]["tech_audit_report"],
        "content_audit_report": content["data"]["outputs"]["content_audit_report"],
        "keyword_gap_report": gap["data"]["outputs"]["gap_report"],
        "keyword_researcher_report": researcher["data"]["outputs"]["keyword_report"],
    })

    master_plan = master["data"]["outputs"]["master_plan"]
    top_keywords = master["data"]["outputs"]["top_keywords_for_briefs"]

    # Stap 3: brief generation per top-keyword
    briefs = []
    for kw in top_keywords[:10]:
        brief = run_workflow("brief_generator", {"hoofdkeyword": kw, "doelgroep": "", "extra_context": ""})
        briefs.append({"keyword": kw, "brief": brief["data"]["outputs"].get("content_brief", "")})

    return {"master_plan": master_plan, "briefs": briefs}


if __name__ == "__main__":
    result = run_master_audit(
        domein="https://dev.energx.nl",
        competitors=["consumentenbond.nl", "milieucentraal.nl"],
        seed_thema="thuisbatterij",
    )
    # Schrijf naar disk + email
    with open("master-plan.md", "w") as f:
        f.write(result["master_plan"])
    print(f"Klaar: master-plan.md + {len(result['briefs'])} briefs")
```

**Inrichten:**
1. Per Dify-app: ga naar de app → API Access (linkermenu) → "Create API Key"
2. Zet keys in `.env` van je orchestrator
3. Cron job die deze script wekelijks draait

### Niveau 3 — Volautomatisch met scheduled task in Dify

Sinds Dify 0.15+ heb je "Scheduled Tasks". In Dify Studio:
1. Open je Master Workflow
2. Settings → Schedule
3. Cron-expressie: bijv. `0 9 * * 1` (elke maandag 9:00)
4. Default inputs configureren

Voor de inputs (de markdown rapporten van A/B/C/D) heeft Dify nog geen
ingebouwde workflow-chaining; dat moet via Niveau 2's orchestrator OF
via Dify's HTTP-request node die de andere workflows aanroept.

---

## PDF generatie

Het master-plan komt uit Dify als markdown. Voor een PDF kun je:

### Optie A — Pandoc op je VPS (gratis, snel)

```bash
# Op je VPS, in je orchestrator:
pip install --user --break-system-packages pypandoc weasyprint
```

Of CLI:
```bash
pandoc master-plan.md -o master-plan.pdf --pdf-engine=weasyprint \
  --metadata title="Energx SEO Master Plan" \
  --css energx-style.css
```

### Optie B — Markdown to PDF endpoint toevoegen aan FastAPI service

Voeg een endpoint `/render/pdf` toe in de audit-service die markdown→PDF
converteert met weasyprint. Dan kun je 'm direct vanuit Dify aanroepen
als HTTP-tool.

### Optie C — Gewoon HTML versturen

Veel pragmatischer: render markdown → HTML in de orchestrator, en stuur
HTML als email-body. Email-clients kunnen dat prima tonen. Geen PDF-fuss.

---

## Email versturen

In de orchestrator (Python):

```python
import smtplib
from email.message import EmailMessage
import markdown  # pip install markdown

def send_master_plan(to: str, subject: str, master_plan_md: str, briefs: list):
    html_body = markdown.markdown(master_plan_md, extensions=['tables'])
    msg = EmailMessage()
    msg["From"] = "info@energx.nl"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(master_plan_md)  # plain text fallback
    msg.add_alternative(f"""
        <html><body>{html_body}</body></html>
    """, subtype="html")

    # Attach briefs als losse markdown bestanden (optioneel)
    for brief in briefs:
        msg.add_attachment(
            brief["brief"].encode(),
            maintype="text",
            subtype="markdown",
            filename=f"brief-{brief['keyword'].replace(' ', '-')}.md",
        )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("info@energx.nl", os.getenv("SMTP_PASSWORD"))  # of app-password
        server.send_message(msg)
```

Gebruik SMTP van je email-provider (Gmail/SendGrid/Postmark/Mailgun). Voor
Energx als eenmanszaak: Gmail SMTP met app-password is gratis en werkt.

---

## Aanbevolen volgorde van implementatie

| Stap | Wat | Tijdsinvestering |
|---|---|---|
| 1 | FastAPI service deployen op VPS | 30 min |
| 2 | Custom tool registreren in Dify | 5 min |
| 3 | Workflow A en B importeren + testen | 30 min |
| 4 | Workflow C en D importeren + testen | 30 min |
| 5 | Workflow E importeren + handmatige Niveau-1 test | 15 min |
| 6 | Python orchestrator schrijven (Niveau 2) | 2-3 uur |
| 7 | Cron + email setup | 30 min |
| **Totaal tot productie-orchestratie** | | **~5 uur** |

---

## Volgende stappen ná Master Workflow

1. **Frontend (Weekend 6)** — Next.js form waar je domein invoert, status pollt, en master-plan terugkrijgt
2. **Multi-tenant transformatie** — andere klanten naast Energx
3. **Klant-aanmeldflow** — payment, billing, account-management
4. **API publiek maken** — Energx API voor integraties

Maar dat zijn allemaal later-zorgen. Eerst: het bovenstaande draait.

---

Versie: 1.0 (mei 2026)
