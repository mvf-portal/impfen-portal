#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/impfen.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "impfen-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
        '(("Vaccination"[Majr] OR "Vaccines"[Majr] OR "Immunization"[Majr] '
        'OR "Immunization Programs"[Majr] OR "Vaccination Coverage"[Majr] '
        'OR "Vaccination Hesitancy"[Majr] OR "Immunization Schedule"[Majr] '
        'OR "Mass Vaccination"[Majr]) '
        'OR (vaccin*[Title] OR immunization[Title] OR immunisation[Title] '
        'OR "vaccine hesitancy"[Title] OR "vaccine uptake"[Title] '
        'OR "vaccination coverage"[Title] OR "herd immunity"[Title]))'
)
_KONTEXT = (
        '("Delivery of Health Care"[MeSH Terms] OR "Health Services"[MeSH Terms] '
        'OR "Quality of Health Care"[MeSH Terms] OR "Patient Care"[MeSH Terms] '
        'OR "Health Policy"[MeSH Terms] OR "Public Health"[MeSH Terms] '
        'OR "health care"[Title/Abstract] OR "health services"[Title/Abstract] '
        'OR "patient outcome*"[Title/Abstract] OR "clinical practice"[Title/Abstract] '
        'OR implementation[Title/Abstract] OR patients[Title/Abstract])'
)
# "Humans"[MeSH] haelt Tier-, Labor- und reine Modellarbeiten heraus.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}) AND "Humans"[MeSH Terms])',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 30
POOL_ALLGEMEIN = 25
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 5
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
        "Du bist Fachredakteur fuer Impfen und Impfpraevention. Aus einer "
        "Liste von PubMed-Abstracts waehlst du die relevantesten aktuellen "
        "Studien aus und fasst sie praezise auf Deutsch zusammen. Deine "
        "Leserschaft arbeitet im deutschen Gesundheitswesen: oeffentlicher "
        "Gesundheitsdienst, Praxen, Kliniken, Kostentraeger, Selbstverwaltung "
        "und Gesundheitspolitik. Sie will wissen, ob eine Impfung in der "
        "Versorgung ankommt - nicht, welcher Antikoerpertiter im Labor "
        "erreicht wurde."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) Impfungen, Impfprogramme, Impfquoten, Impfbereitschaft oder die Sicherheit von Impfstoffen untersuchen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
      1. Wirkung in der Versorgung: Impfeffektivitaet unter Alltagsbedingungen,
         verhinderte Erkrankungen, Krankenhauseinweisungen oder Todesfaelle -
         gemessen an Bevoelkerungsdaten, nicht an Laborwerten.
      2. Erreichbarkeit und Quote: Was hebt die Durchimpfung? Erinnerungs- und
         Einladungsverfahren, aufsuchende Angebote, Impfen in Apotheke, Schule
         oder Betrieb, Abrechnungs- und Zugangshuerden.
      3. Vertrauen und Entscheidung: Impfbereitschaft, Beratungsformate,
         Umgang mit Skepsis, Wirkung von Kampagnen und Kommunikation.
      4. Sicherheit: Pharmakovigilanz, Signalbewertung, Studien zu
         unerwuenschten Ereignissen mit belastbarer Vergleichsgruppe.
      5. Programm und System: Impfkalender, Empfehlungen, Kosten-Nutzen-
         Bewertungen, Impfpflicht und ihre Folgen, Register und Meldewesen.
      6. Ungleichheit: Wer bleibt ungeimpft - nach Einkommen, Bildung,
         Sprache, Region, Migrationsgeschichte - und was hilft dagegen.

NICHT in die Auswahl gehoeren:
praeklinische Immunologie und Impfstoffentwicklung im Labor, Studien, die allein Antikoerpertiter oder Immunogenitaet ohne klinischen Endpunkt berichten, Phase-I-Studien, Erregergenomik und Sequenzanalysen, reine Modellrechnungen ohne empirische Grundlage, Querschnittsbefragungen ohne Bezugsgroesse ("X Prozent waeren bereit"), sowie Uebersichten, die nichts Eigenes berichten.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
      1. MINDESTENS DREI der sechs Studien muessen aus Europa stammen oder ein
         europaeisches Gesundheitssystem betreffen. Liegen weniger als drei solche
         Arbeiten vor, nimm die verbleibenden Plaetze aus dem Rest - aber schoepfe
         die europaeischen zuerst aus.
      2. HOECHSTENS EINE der sechs darf sich ausschliesslich mit Praevention
         OHNE Impfbezug befassen - Frueherkennung, Screening, Gesundheits-
         foerderung. Praevention ist hier der Zusammenhang, nicht das Thema:
         Ohne diese Grenze waere der Hub binnen weniger Wochen ein zweites
         Gesundheitskompetenz-Portal, denn dort liegt dieses Material bereits.
      3. HOECHSTENS EINE darf eine digitale Anwendung im Mittelpunkt haben
         (App, Portal, Erinnerungssystem per SMS, Sprachmodell). Solche Arbeiten
         deckt das Schwesterportal ki.m-vf.de ab; zugelassen ist die Studie nur,
         wenn die Impffrage im Vordergrund steht, nicht die Technik.
      4. HOECHSTENS EINE darf ausschliesslich eine Impfquote beschreiben, ohne
         eine Massnahme, eine Ursache oder eine Folge zu untersuchen.
      5. HOECHSTENS ZWEI der sechs duerfen COVID-19 betreffen. Der Anteil am
         Kandidatenpool lag am 19.08.2026 bei 28,2 Prozent und im Jahr davor
         bei 37,5 Prozent - er sinkt, ist aber gross genug, dass an einem
         Spitzentag die halbe Ausgabe aus Corona-Arbeiten bestuende. Zwei ist
         bewusst nicht eins: Bei rund einem Viertel des Materials waere eine
         schaerfere Grenze keine Ausgewogenheit mehr, sondern Unterdrueckung
         eines Themas, das die Leserschaft weiterhin betrifft.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Ein Impfprogramm haengt am System, das es traegt. Massgeblich sind der nationale Impfkalender, die Frage, wer impfen darf (in Deutschland seit 2022 auch Apotheken, anderswo laengst Pflegekraefte), die Abrechnung und ob es ein Impfregister gibt - Deutschland hat keines, die Niederlande und Skandinavien haben eines, was ihre Quotendaten unvergleichbar genau macht. Ordne die Systeme nach Vergleichbarkeit: hoch bei DACH, Niederlanden, Belgien und Frankreich, mittel bei Skandinavien, Grossbritannien, Kanada und Australien, gering bei den USA. Nenne im Feld transfer ausdruecklich, woran die Uebertragbarkeit haengt - meist am Zugangsweg oder am Registerwesen.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel.
      **Er MUSS mit der Impf- oder Versorgungsfrage beginnen, nicht mit dem
      Erreger.** Fast jede Arbeit haengt an einer konkreten Krankheit - Masern,
      Influenza, HPV -, und die Abstracts sind danach betitelt. Uebernimmt der
      Titel das, liest sich der Hub wie eine infektiologische Sammlung. Nicht
      "Masernausbruch in Rumaenien: ...", sondern
      "Impfluecken bei Jugendlichen fuehrten zu ...".
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Beispiele fuer Begriffe, die englisch bleiben: Vaccine Hesitancy (neben Impfskepsis), Zero-Dose, Cocooning, Catch-up. Uebersetze dagegen, was im Deutschen eine gaengige Entsprechung hat: aus "vaccination coverage" wird die Impfquote, aus "booster" die Auffrischimpfung, aus "herd immunity" die Herdenimmunitaet, aus "breakthrough infection" die Durchbruchinfektion.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""
