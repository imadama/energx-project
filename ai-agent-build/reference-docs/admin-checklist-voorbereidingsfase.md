# Admin-checklist Voorbereidingsfase

> Concrete stappen die Imad zelf moet doen vóór weekend 1. Tijd: ongeveer 1 uur als alles meezit. Doe deze in volgorde — sommige hebben elkaar nodig.

---

## 1. Anthropic API account + spend limit (10 min)

### Stappen

1. **Account aanmaken** (als je 'm nog niet hebt):
   - Ga naar https://console.anthropic.com/
   - Sign up met `imadamazyan@gmail.com` (of zakelijke mail als je die liever wilt)
   - Verifieer e-mail

2. **Billing toevoegen:**
   - Console → Settings → Billing
   - Voeg een credit card of factuur-route toe
   - Eerste storting: **€30 prepaid** is genoeg voor weekend 1 + 2 testen

3. **Spend limit instellen** (cruciaal — voorkomt verrassingen):
   - Settings → Limits
   - Set **monthly spend limit: €100** (start)
   - Set **email alert at: €50** (early warning)
   - Bewaar deze limieten en pas omhoog als je weet wat je verbruik is

4. **API key aanmaken:**
   - Settings → API Keys → "Create Key"
   - Naam: `dify-production` (of `energx-dify`)
   - Type: standard
   - **Kopieer de key direct** — je krijgt 'm maar één keer te zien
   - Bewaar in een password manager (1Password, Bitwarden), niet in plain text

### Wat je krijgt
Een key zoals `sk-ant-api03-...` die je in Dify gaat plakken bij de Anthropic provider config.

### Cost check (referentie)
- Claude Sonnet 4.6: ~$3/Mtok input, ~$15/Mtok output
- Eén content brief generatie: ~$0.05-0.15 per brief
- €30 = ongeveer 200-300 briefs of veel debug-runs

---

## 2. Google Search Console verifiëren voor dev.energx.nl (30 min)

### Stappen

1. **Login Search Console:**
   - Ga naar https://search.google.com/search-console
   - Login met het Google-account dat Energx beheert (niet je persoonlijke als die anders is)

2. **Property toevoegen:**
   - Klik "Add property" linksboven
   - **Belangrijk:** kies **URL prefix** (niet Domain) voor `https://dev.energx.nl/`
   - Klik "Continue"

3. **Verifiëren — kies één methode:**

   **Optie A: HTML-file upload (eenvoudigst voor dev-site)**
   - Download het HTML-bestand dat Google geeft
   - Upload naar de root van dev.energx.nl (bijv. via FTP/SFTP/Coolify volumes)
   - Check dat het bereikbaar is via `https://dev.energx.nl/google[unieke-code].html`
   - Klik "Verify" in GSC

   **Optie B: HTML-tag**
   - Google geeft een `<meta>` tag
   - Plak in de `<head>` van je homepage
   - Deploy, dan "Verify"

   **Optie C: DNS TXT-record**
   - Voor heel dev.energx.nl, niet aan te raden voor een dev-omgeving

4. **Wacht op data:**
   - Na verificatie: het kan 24-48 uur duren voor er data verschijnt
   - Voor weekend 1 hebben we waarschijnlijk genoeg data van de gepubliceerde blog

5. **Maak een Service Account voor API-toegang** (voor Dify-integratie weekend 1):
   - Ga naar https://console.cloud.google.com/
   - Project: maak nieuw project "energx-seo-agent" als nog niet bestaat
   - Enable de **Google Search Console API**
   - Maak een Service Account aan
   - Genereer JSON-credentials (download het bestand, bewaar veilig)
   - **Belangrijk:** voeg het service account email als user toe in Search Console → Settings → Users (met "Restricted" permission is genoeg)

### Wat je krijgt
- Toegang tot rankingsdata van dev.energx.nl
- Een JSON-credentials-bestand voor Dify-integratie

### Risico's
- **Google OAuth setup kan 2-3 uur duren** als je niet eerder met Cloud Console hebt gewerkt — daarom dit zaterdag-vroeg doen
- **Verificatie HTML-bestand:** soms helpt het om eerst in een privé-tab te checken of de URL bereikbaar is voor je op "Verify" klikt

---

## 3. Dify volledige backup maken (15 min)

### Stappen

Vanaf je VPS (SSH):

```bash
# Stop Dify containers voor consistente backup
cd /pad/naar/dify/docker
docker compose stop

# Backup de volumes
sudo tar czf ~/dify-backup-$(date +%Y%m%d-%H%M).tar.gz \
  ./volumes \
  ./.env \
  ./docker-compose.yaml

# Of als je Coolify gebruikt:
# - In Coolify dashboard: Application → Backups → "Manual backup"

# Start Dify weer
docker compose start

# Verify backup bestand
ls -lh ~/dify-backup-*.tar.gz
```

### Alternatief — via Coolify MCP

Als je Coolify gebruikt (lijkt zo), dan kan ik vanaf hier het backup-proces ondersteunen:
- Ik kan de containers stoppen via `mcp__coolify__control`
- Ik kan een snapshot van de volumes maken via Coolify backups feature
- Vertel het, dan doe ik 'm

### Waar de backup bewaren
- **NIET op dezelfde VPS** — als de schijf crasht, ben je 'm kwijt
- Liefst: kopieer naar externe locatie (Backblaze B2, S3, Hetzner Storage Box, of een tweede VPS)
- Snelle route: `scp` naar je laptop voor nu, externe storage komt weekend 1

```bash
# Lokaal op je laptop:
scp gebruiker@vps:~/dify-backup-*.tar.gz ~/Documents/energx-backups/
```

### Wat je krijgt
- Een werkende fallback als er iets misgaat in weekend 1
- Een naam-met-datum backup zodat je weet wanneer je 'm hebt gemaakt

---

## 4. System prompt fix in Brief Generator (5 min)

### Stappen

1. Open de file `brief-generator-system-prompt.md` (apart deliverable)
2. Kopieer de prompt-tekst tussen `---BEGIN---` en `---EIND---`
3. Login op je Dify-instantie
4. Ga naar de Content Brief Generator workflow
5. Selecteer de **Brief Generator LLM-node** (de laatste, die de markdown brief output)
6. Vervang de huidige system prompt door v2
7. Save de workflow
8. Run een test met keyword `thuisbatterij kopen`
9. Vergelijk output met de huidige live blog — moet vergelijkbaar of beter zijn

### Belangrijk
Vóór het plakken van v2: **maak een kopie van de huidige workflow** in Dify (rechtsboven → "Duplicate"). Dan heb je een fallback.

### Wat je krijgt
- Een v2 Brief Generator die KB-aware is in plaats van hardcoded
- Hallucination-checks ingebouwd
- Output die strakker geformatteerd is voor downstream gebruik

---

## 5. Documenten review en voorbereiden (60-90 min)

### Stappen

1. **Document C reviewen** — open `review-docs-c-en-d.md`, doorloop de MUST-fixes (3 stuks)
   - Verifieer EVOI/VESP certificeringen
   - Update stroomprijs-range
   - Eventueel: doe de nice-to-have fixes
2. **Document D reviewen** — zelfde, doorloop MUST-fixes (2 stuks)
   - INP-threshold corrigeren
   - FAQPage-disclaimer toevoegen
3. **Document A finaliseren** — open `document-a-energx-tone-of-voice.md`, vul `<!-- ENERGX -->` secties aan met:
   - Doelgroep-details die jij weet
   - Bedrijfspositionering / brand-belofte als je die hebt
4. **Document B finaliseren** — open `document-b-energx-bedrijfsprofiel.md`, vul `<!-- INVULLEN -->` secties aan met:
   - KvK, BTW, oprichtingsjaar
   - Contact-gegevens
   - USPs die je kunt onderbouwen
   - Partner-netwerk grootte (als publiek bekend)
   - Brand-assets

### Wat je krijgt
- 4 KB-documenten klaar voor upload in Dify weekend 1
- Versie 1.0 / 1.1 zoals jij bepaalt

---

## Checklist eindcheck

Voor je weekend 1 begint, dit moet allemaal `done`:

- [ ] Anthropic API key in password manager
- [ ] Spend limit ingesteld (€100/maand + €50 alert)
- [ ] Google Search Console verified voor dev.energx.nl
- [ ] Service Account JSON-credentials gedownload en bewaard
- [ ] Dify backup gemaakt en op aparte locatie bewaard
- [ ] Brief Generator v2 prompt in productie (of als kopie naast v1)
- [ ] Document C: MUST-fixes doorgevoerd
- [ ] Document D: MUST-fixes doorgevoerd
- [ ] Document A: ENERGX-secties ingevuld
- [ ] Document B: INVULLEN-secties ingevuld

---

## Wat ik intussen kan doen

Terwijl je de admin-taken doet, kan ik vast:

1. **Workflow A (Tech Audit) DSL schrijven** — Dify YAML klaar voor import weekend 2-3
2. **FastAPI audit-service code schrijven** — Docker-ready Python service voor weekend 2
3. **Workflow B (Content Audit) DSL schrijven** — Dify YAML voor weekend 3
4. **Brief Generator: bestaande versie reverse-engineeren** — als je 'm exporteert als DSL, kan ik 'm naast v2 leggen

Welke wil je dat ik als eerste oppak?
