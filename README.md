# Impfen & Impfprävention · Rechercheportal

Ein Rechercheportal zum Themenfeld **Impfen & Impfprävention**: 96 Datenbanken in 10 Rubriken,
davon 50 mit Live-Suche, dazu eine täglich aus PubMed kuratierte Studienauswahl mit
deutschen Zusammenfassungen.

Ein Angebot von **Monitor Versorgungsforschung** (eRelation AG – Content in Health, Bonn).

https://impfen.m-vf.de/

## Wie es funktioniert

Ein Suchbegriff, eingegeben an einer Stelle, stellt sämtliche Datenbankkacheln darauf ein;
ein Klick führt direkt in die Trefferliste der jeweiligen Datenbank. Deutsche Fachbegriffe
werden für internationale Datenbanken automatisch in den Ausdruck übersetzt, unter dem sie
dort indexiert sind (163 Begriffe).

| | |
|---|---|
| Datenbanken | 96 in 10 Rubriken |
| Live-Suche | 50 |
| Portal (feste URL) | 41 |
| Lizenz nötig | 5 |
| Suchglossar | 163 Begriffe |
| Studienauswahl | täglich 6 Uhr aus PubMed, KI-kuratiert |

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | die gesamte Anwendung (CSS + HTML + JS inline) |
| `ueber.html`, `newsletter.html` | Begleitseiten |
| `scripts/thema.py` | **alles Themenspezifische** der Studienauswahl |
| `scripts/update_studies.py` | PubMed → Claude → Marker-Block (in allen Portalen gleich) |
| `scripts/build_newsletter.py` | RSS-Feed und Download-Dateien aus dem Archiv |
| `scripts/mailchimp_entwurf.py` | Kampagnen-Entwurf zur Freigabe |
| `studien-archiv.json` | vollständige Historie aller gezeigten Studien |
| `portal.json` | die Werte dieses Portals — Grundlage des Vorlagen-Abgleichs |

Dieses Portal ist aus der Vorlage `mvf-portal/portal-vorlage` entstanden. Änderungen an der
Mechanik gehören dorthin und werden von dort in alle Portale eingespielt.

## Betrieb

Kein Build, kein Framework. Commit auf `main` → GitHub Pages baut automatisch.

Secrets im Repository: `IMPFHUB` (Claude-API) und `IMPFHUBMC` (Mailchimp).
