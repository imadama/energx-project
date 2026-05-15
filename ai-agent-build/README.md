# Energx SEO Agent — Build folder

Alle deliverables van de AI-agent build, gegenereerd in chat-sessies.

## Structuur

- **kb-documents/** — Knowledge Base bestanden voor Dify (4 docs, FINAL versies, klaar voor upload)
- **dify-workflows/** — 5 Dify workflow DSLs (A=tech, B=content, C=gap, D=researcher, E=master) + orchestratie-guide
- **audit-service/** — FastAPI microservice
  - `source/` — alle Python broncode
  - `energx-audit-service.tar.gz` — deployment-tarball (16KB, klaar voor scp naar VPS)
- **reference-docs/** — prompts, admin-checklists, KB-doc reviews
- **energx-seo-agent-roadmap-v1.1.md** — geüpdate roadmap met huidige progress

## Status

Productie:
- KB live in Dify
- Brief Generator v2 met KB-binding

Code klaar (nog deployen):
- FastAPI audit-service (zie `audit-service/source/README.md`)
- 5 Dify workflow DSLs (zie `dify-workflows/MASTER-ORCHESTRATION-GUIDE.md`)

Versie: 1.0 (mei 2026)
