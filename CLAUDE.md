# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Wat is dit?
Website voor Energx.nl — een Nederlands duurzame energie bedrijf dat thuisbatterijen, laadpalen en warmtepompen aanbiedt via lokale installateurs.

## Stack
Statische HTML/CSS/JS met Vite als build tool. Geen framework, geen JS-runtime in de browser.

## Commando's
```bash
npm run dev      # dev server op http://localhost:5173 met hot reload
npm run build    # productie-build naar /dist
npm run preview  # preview van de /dist build
```

## Architectuurpatronen

### CSS-variabelen (in elke pagina `<style>`)
Alle kleur- en typografie-tokens staan in `:root` bovenaan elke `<style>`-block. Gebruik uitsluitend deze variabelen — geen hardcoded hex-waarden:
- `--green-800` (#0F4A2A) — primair, knoppen, nav
- `--green-400` (#2DBD6E) — accent, highlights
- `--night` (#090F0C) — donkere achtergronden
- `--font-display`: DM Serif Display (koppen)
- `--font-body`: Outfit (bodytekst)
- `--max: 1200px` — max-width voor content containers
- `--radius: 16px`, `--radius-sm: 10px`

### Paginastructuur (index.html en productpagina's)
Elke pagina volgt dezelfde volgorde: `<nav>` (fixed, glassmorphism) → hero → feature-secties → social proof → CTA → `<footer>`. Productpagina's hebben een offerteformulier als hoofdconversie-element.

### Offerteformulier (energx-laadpaal.html)
Multi-step wizard volledig in vanilla JS. Stappen worden getoond/verborgen via CSS `display` op `.step`-elementen. Stap 2 heeft conditionele sub-vragen afhankelijk van de gekozen installatiesituatie. Zie CLAUDE.md sectie "Offerteformulier laadpaal — logica" voor de volledige beslissingsboom.

### Nieuwe productpagina aanmaken
Kopieer `energx-laadpaal.html` als template. Pas aan: `<title>`, hero-tekst, productnaam, merken, en de formulierlogica in stap 1. De nav, footer, CSS-variabelen en basisstijlen zijn identiek.

## Branding
- Primaire kleur: #0F4A2A (bosgroen)
- Accent: #2DBD6E (helder groen)
- Achtergrond donker: #090F0C
- Fonts: DM Serif Display (display/koppen) + Outfit (body)

## Bestanden
- `index.html` — Hoofdpagina / landingspagina
- `energx-laadpaal.html` — Laadpaal productpagina met slim meertraps offerteformulier

## Laadpaal merken
- Ratio (slim & betaalbaar)
- Zaptec (premium, V2G ready)

## Offerteformulier laadpaal — logica
Stap 1: Laadpunt wensen (geld verdienen, zonnestroom, V2G, laadpas)
Stap 2: Installatie situatie:
  - Direct achter meterkast → vraag ruimte aardlekautomaat
  - Kruipruimte & gevel → vraag ruimte aardlekautomaat + afstand
  - Kruipruimte met graafwerk → vraag ruimte aardlekautomaat + afstand + meters graafwerk
Stap 3: Contactgegevens

## Hoe we werken verhaal
Lokale installateurs zijn beter dan grote nationale bedrijven omdat:
- Snelle beschikbaarheid
- Gecertificeerd vakmanschap
- Persoonlijk contact na installatie
- Kennis van lokale subsidies en regelgeving

## Nog te doen
- Thuisbatterij pagina (zelfde opzet als laadpaal pagina)
- Warmtepomp pagina (zelfde opzet als laadpaal pagina)
- Foto's van installaties toevoegen aan laadpaal pagina (foto-grid placeholders staan er al)
- Offerteformulieren koppelen aan backend / e-mail service
- FAQ sectie toevoegen
- SEO meta tags uitbreiden
- Google Analytics / Meta Pixel toevoegen
- Mobiele navigatie (hamburger menu) bouwen
- Netlify / Vercel deployment opzetten
