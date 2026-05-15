# Review Documenten C en D — concrete fixes

> Per fix: wat staat er nu, wat moet het worden, en waarom. Voor toepassing in de huidige documenten. Sommige zijn must-fix (feitelijk onjuist of risico op hallucination-amplificatie), andere zijn nice-to-have.

---

## Document C — NL Energie-feiten

### MUST-FIX 1: Certificeringen "EVOI" en "VESP" verifiëren

**Sectie 6, regels 158-159**

**Probleem:** "EVOI" en "VESP" als certificeringen herken ik niet als gevestigde keurmerken in de NL-installatiebranche. Dit is precies het soort fout dat sectie 12.1 van Doc D zegt te voorkomen ("verzonnen certificeringen").

**Voorgestelde actie:**
- Verifieer beide via een ledenlijst van Techniek Nederland of via Google "[certificering] erkenning"
- Indien niet verifieerbaar: vervangen door wel-bestaande termen
- Veilige alternatieven die we wél zeker weten: **InstallQ**, **Zonnekeur**, **F-gassen-certificaat (BRL 100)**, **Erkend Duurzaam (Nederland Duurzaam)**, **Sterkin**, **OK CV**

**Voorgestelde herschrijving van de tabel:**

```markdown
| Certificering | Waarvoor | Geldt |
|---|---|---|
| **InstallQ** | Algemeen erkenning installatiebranche | actief, breed |
| **Zonnekeur** | Specifiek voor zonnepanelen-installateurs | actief keurmerk |
| **Erkend Duurzaam** | Duurzaamheidsadviseurs/installateurs (Nederland Duurzaam) | actief |
| **Sterkin** | Erkenning voor gas/water-installateurs | actief |
| **F-gassen-certificaat (BRL 100)** | Verplicht voor warmtepomp-installatie | wettelijk vereist |
| **Techniek Nederland** | Branchevereniging (lidmaatschap, geen keurmerk) | bestaat |
```

---

### MUST-FIX 2: Stroomprijs-range splitsen (vast vs variabel)

**Sectie 1, regel 19 + sectie 11, regel 282**

**Probleem:** "€0,28 - €0,34 per kWh" is een wat hoge range voor mei 2026. Vaste contracten zitten in 2026 vaker tussen €0,25 en €0,30. Variabele kunnen pieken bij €0,35+. Door één range te geven zonder onderscheid kun je in content fout zitten.

**Voorgestelde herschrijving:**

```markdown
- Marktprijs stroom (2026, indicatief):
  - **Vast contract:** €0,25 - €0,30 per kWh
  - **Variabel/dynamisch:** sterk wisselend, gemiddeld €0,22 - €0,32 per kWh, met pieken hoger
  - **All-in (incl. belastingen):** doorgaans €0,28 - €0,34 per kWh
```

Voeg toe: "Verifieer actuele tarieven via een vergelijkingssite of een recente energienota voor specifieke claims in content."

---

### NICE-TO-HAVE 3: Saldering — afbouw-narratief expliciter

**Sectie 1, "Veelgemaakte fouten", regel 23**

**Probleem:** "Salderingsregeling wordt afgebouwd — die afbouw-fase is van een eerder voorstel dat niet doorging" — dit is technisch correct maar veel content claimde wél een afbouw. Voor een hallucination-base zou je expliciet kunnen maken dat er hierover beleidsmatige onduidelijkheid is geweest.

**Voorgestelde toevoeging:**

> Historische context (voor zelfcheck bij content): er waren eerder politieke voorstellen om saldering geleidelijk af te bouwen vanaf 2023. Deze voorstellen zijn niet aangenomen. Het huidige beleid is: tot en met 31 december 2026 volledig salderen, vanaf 1 januari 2027 stop. Als oudere bronnen iets anders zeggen, klopt het niet meer.

---

### NICE-TO-HAVE 4: Hybride warmtepomp-norm 2026 actualiseren

**Sectie 9, regel 249-250**

**Probleem:** "Vanaf 2026 is hybride warmtepomp norm bij vervanging cv-ketel (uitgesteld door politiek, check actuele status)" — dat is goed dat er een check-disclaimer staat, maar het kan scherper.

**Voorgestelde herschrijving:**

> **Status mei 2026:** de oorspronkelijke wettelijke verplichting om bij cv-ketel-vervanging te kiezen voor een hybride warmtepomp of duurzaam alternatief is in 2024 ingetrokken. Er bestaat momenteel **geen wettelijke verplichting** voor huishoudens. Wel: aansluitplicht op aardgas geldt niet meer voor nieuwbouw, en grootschalige isolatie- en warmtepomp-programma's lopen via ISDE en het Warmtefonds. Verifieer bij content over verplichtingen altijd op rijksoverheid.nl.

---

### NICE-TO-HAVE 5: Anglicisme-tabel rij "compensation" herschrijven

**Sectie 12, regel 309**

**Probleem:** In de "Liever niet"-kolom staat `"wederopname" (= geen NL woord)` — dat is verwarrend voor een LLM die deze rij gebruikt. De rij hoort te zijn: Engels woord → wat te vermijden → wat wel.

**Voorgestelde herschrijving:**

```markdown
| Compensation | "wederopname" (geen bestaand NL woord), "compensatie" (te vaag in deze context) | "vergoeding" of "verrekening" (afhankelijk van context) |
```

---

## Document D — NL SEO-richtlijnen

### MUST-FIX 1: INP-threshold corrigeren

**Sectie 11, regel 373-374**

**Probleem:** "FID/INP: < 100ms" — dit klopt niet meer.
- FID is uitgefaseerd door Google (maart 2024)
- INP is sinds maart 2024 de officiële Core Web Vital
- INP-threshold is **200ms** (good), niet 100ms
  - "Needs improvement" = 200-500ms
  - "Poor" = >500ms

**Voorgestelde herschrijving:**

```markdown
### Page speed (mobiel)
- Core Web Vitals targets (per maart 2024):
  - **LCP** (Largest Contentful Paint): < 2.5s
  - **INP** (Interaction to Next Paint): < 200ms — heeft FID per maart 2024 vervangen
  - **CLS** (Cumulative Layout Shift): < 0.1
```

---

### MUST-FIX 2: FAQPage rich result-selectiviteit melden

**Sectie 8, regel 284-288**

**Probleem:** Google heeft in augustus 2023 aangekondigd dat FAQPage rich snippets alleen nog tonen voor "well-known, authoritative government and health websites". Voor commerciële sites is FAQPage-markup nog wel geldig, maar levert nauwelijks rich-snippet-tooning op.

**Voorgestelde toevoeging onder sectie 8 FAQPage:**

> **Status mei 2026:** Sinds augustus 2023 toont Google FAQPage rich snippets alleen nog op een zeer beperkt aantal autoriteits-sites (overheid, gezondheidszorg). Voor commerciële sites zoals Energx is FAQPage-schema dus voornamelijk waardevol voor:
> - Bing en andere zoekmachines (die nog wel rich snippets tonen)
> - Toekomstige beleidswijzigingen door Google
> - Structuurinformatie voor AI-zoekmachines (Perplexity, SearchGPT)
>
> Het opnemen blijft aanbevolen maar overbelast er geen content voor.

---

### NICE-TO-HAVE 3: Lijdende vorm vs naamwoordstijl scheiden

**Sectie 9, regel 318**

**Probleem:** De huidige tekst noemt "naamwoordstijl" als voorbeeld onder "Lijdende vorm vermijden" — dat zijn twee verschillende fenomenen, kan verwarrend zijn voor een LLM.

**Voorgestelde herschrijving:**

```markdown
### Praktische regels voor NL readability
- **Gemiddelde zinslengte:** 12-18 woorden
- **Woorden per paragraaf:** max 80
- **Lijdende vorm vermijden** ("wordt geïnstalleerd" → "installateur installeert")
- **Naamwoordstijl vermijden** ("het uitvoeren van de installatie" → "de installatie uitvoeren")
- **Substantiveringen vermijden** ("een verbetering van" → "verbeterde")
```

---

### NICE-TO-HAVE 4: E-E-A-T sectie toevoegen

**Nieuwe sectie tussen 12 en 13 toevoegen**

**Probleem:** E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) is sinds 2022-2023 een belangrijk Google-signaal, vooral voor "Your Money or Your Life" (YMYL)-content. Energie/subsidie-content valt onder YMYL.

**Voorgestelde toevoeging:**

```markdown
## 12.5. E-E-A-T voor YMYL-content (Your Money or Your Life)

Google beoordeelt energie-/financiële content extra streng op:

### Experience (ervaring)
- Concrete praktijkvoorbeelden ("In een rijtjeshuis uit jaren '70 zien we vaak...")
- Casus-getuigenissen waar mogelijk
- "Wij hebben dit honderden keren gezien"-statements alleen als waar

### Expertise (deskundigheid)
- Author-bio per artikel met relevante kennis
- Verwijzing naar bronnen (RVO, branche-organisaties)
- Vaktermen correct gebruiken (na uitleg)

### Authoritativeness (autoriteit)
- Backlinks van energie-/duurzaamheid-branchemedia
- Vermelding in onafhankelijke vergelijkingsbronnen
- Branche-keurmerken visueel tonen

### Trustworthiness (vertrouwen)
- Transparante prijsranges (geen lokvogeltjes)
- Disclaimers bij subsidies en bedragen
- Heldere "wie wij niet zijn"-communicatie
- Contactgegevens duidelijk op site
- Privacy- en cookieverklaring up-to-date

> **Schrijfregel:** voor elk YMYL-artikel, check minstens 3 van de bovenstaande punten expliciet in.
```

---

### NICE-TO-HAVE 5: AI-search optimalisatie (kort)

**Tussen sectie 10 en 11 toevoegen**

**Probleem:** Perplexity, ChatGPT-search, Claude, Google AI Overviews zijn nieuwe traffic-bronnen. Content-strategie zou hierop moeten anticiperen.

**Voorgestelde toevoeging:**

```markdown
## 10.5. AI-search optimalisatie

### Anders dan Google
AI-zoekmachines (Perplexity, ChatGPT, AI Overviews) citeren content vaak letterlijk in antwoorden. Optimalisatie:

- **Definities direct en kort** — eerste paragraaf onder een vraag-H2 is wat geciteerd wordt
- **Lijsten met genummerde stappen** — AI's herkennen en hergebruiken deze structuur
- **Concrete getallen met bron** — "Volgens RVO is de ISDE-subsidie voor hybride warmtepompen €2.100-€2.500 in 2026"
- **Niet over-promoten** — AI's filteren marketing-taal eruit, feiten blijven over

### Schema voor AI-search
- Article-schema met `author` en `publisher` (auteurschap-signaal)
- `mainEntity` waar passend (FAQ, HowTo)
- `dateModified` actueel houden — verouderde content wordt minder geciteerd

### Test je content
- Stel de hoofdvraag van een artikel in Perplexity: word je geciteerd?
- Test in Claude/ChatGPT: hoe wordt jouw content samengevat?
- Itereer op basis van wat citeerwaardig blijkt
```

---

## Prioriteit-overzicht

| Fix | Document | Prioriteit | Tijd om door te voeren |
|---|---|---|---|
| Certificeringen EVOI/VESP verifiëren | C | MUST | 30 min (verificatie) + 5 min edit |
| Stroomprijs-range splitsen | C | MUST | 5 min |
| Saldering historische context | C | NICE | 5 min |
| Hybride warmtepomp-norm actualiseren | C | NICE | 5 min |
| Compensation-rij herschrijven | C | NICE | 2 min |
| INP-threshold corrigeren | D | MUST | 5 min |
| FAQPage rich-result disclaimer | D | MUST | 5 min |
| Lijdende vorm + naamwoordstijl scheiden | D | NICE | 3 min |
| E-E-A-T sectie toevoegen | D | NICE | 15 min |
| AI-search optimalisatie sectie | D | NICE | 15 min |

**Totaal:** ~95 minuten voor alle fixes inclusief verificatie

---

## Wat ik aanbeveel

1. **Doe de MUST-fixes nu** — feitelijk onjuist of zou hallucination-cascade kunnen veroorzaken
2. **Verifieer EVOI/VESP** vóór upload naar Knowledge Base (deze kan je echt niet verkeerd hebben — staat in een fact-base)
3. **NICE-to-haves bewaren voor weekend 1** — niet blokkerend voor upload, wel beter binnen 1-2 weken doorvoeren
4. **Versie-nummer bumpen** naar 1.1 als deze fixes erin staan, voor traceability

Wil je dat ik de gefixte versies van C en D direct schrijf zodat je ze gewoon kunt vervangen? Dat scheelt jou de copy-paste werk.
