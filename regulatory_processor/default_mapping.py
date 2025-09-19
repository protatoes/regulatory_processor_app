"""Built-in default mapping table for document processing."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

COLUMN_NAMES: List[str] = [
    "Country",
    "Language",
    "National reporting system SmPC",
    "Line 1 - Country names to be bolded - SmPC",
    "Line 2 - SmPC",
    "Line 3 - SmPC",
    "Line 4 - SmPC",
    "Line 5 - SmPC",
    "Line 6 - SmPC",
    "Line 7 - SmPC",
    "Line 8 - SmPC",
    "Line 9 - SmPC",
    "Line 10 - SmPC",
    "Hyperlinks SmPC",
    "Link for email - SmPC",
    "National reporting system PL",
    "Text to be appended after National reporting system PL",
    "Hyperlinks PL",
    "Country names to be bolded - PL",
    "Link for email - PL",
    "Local Representative",
    "Country names to be bolded - Local Reps",
    "Annex I Date Format",
    "Annex IIIB Date Format",
    "Original text national reporting - SmPC",
    "Text link to be deactivated",
    "Annex I Date Header",
    "Annex IIIB Date Text",
    "Annex I Header in country language",
    "Annex II Header in country language",
    "Annex IIIB Header in country language",
    "Original text national reporting - PL",
    "Text to be moved to the next line",
    "Country Group",
    "Product",
]

DEFAULT_MAPPING_ROWS: List[Dict[str, str]] = [
    {
        "Country": "België/Nederland",
        "Language": "Dutch",
        "National reporting system SmPC": """België
Federaal Agentschap voor Geneesmiddelen en Gezondheidsproducten
www.fagg.be
Afdeling Vigilantie:
Website: www.eenbijwerkingmelden.be
e-mail: adr@fagg-afmps.be

Nederland
Nederlands Bijwerkingen Centrum Lareb
Website: www.lareb.nl""",
        "Line 1 - Country names to be bolded - SmPC": "België;Nederland",
        "Line 2 - SmPC": "Federaal Agentschap voor Geneesmiddelen en Gezondheidsproducten; Nederlands Bijwerkingen Centrum Lareb",
        "Line 3 - SmPC": "www.fagg.be; Website: www.lareb.nl",
        "Line 4 - SmPC": "Afdeling Vigilantie:;",
        "Line 5 - SmPC": "Website: www.eenbijwerkingmelden.be;",
        "Line 6 - SmPC": "e-mail: adr@fagg-afmps.be;",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.fagg.be;www.eenbijwerkingmelden.be;www.lareb.nl",
        "Link for email - SmPC": "adr@fagg-afmps.be",
        "National reporting system PL": """België
Federaal Agentschap voor Geneesmiddelen en Gezondheidsproducten
www.fagg.be
Afdeling Vigilantie:
Website: www.eenbijwerkingmelden.be
e-mail: adr@fagg-afmps.be

Nederland
Nederlands Bijwerkingen Centrum Lareb
Website: www.lareb.nl""",
        "Text to be appended after National reporting system PL": "Door bijwerkingen te melden, kunt u ons helpen meer informatie te verkrijgen over de veiligheid van dit geneesmiddel.",
        "Hyperlinks PL": "www.fagg.be;www.eenbijwerkingmelden.be;www.lareb.nl",
        "Country names to be bolded - PL": "België;Nederland",
        "Link for email - PL": "adr@fagg-afmps.be",
        "Local Representative": """België
Regeneron Ireland DAC
Tél/Tel: 0800 89383

Nederland
Regeneron Ireland DAC
Tel: 0800 020 0943""",
        "Country names to be bolded - Local Reps": "België;Nederland",
        "Annex I Date Format": "dd month yyyy",
        "Annex IIIB Date Format": "month yyyy",
        "Original text national reporting - SmPC": "het nationale meldsysteem zoals vermeld in aanhangsel V.",
        "Text link to be deactivated": "aanhangsel V;www.fagg.be",
        "Annex I Date Header": "DATUM VAN HERZIENING VAN DE TEKST",
        "Annex IIIB Date Text": "Deze bijsluiter is voor het laatst goedgekeurd in",
        "Annex I Header in country language": "BIJLAGE I",
        "Annex II Header in country language": "BIJLAGE II",
        "Annex IIIB Header in country language": "B. BIJSLUITER",
        "Original text national reporting - PL": "het nationale meldsysteem zoals vermeld in aanhangsel V.",
        "Text to be moved to the next line": "De volgende informatie is alleen bestemd voor beroepsbeoefenaren in de gezondheidszorg:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Belgique/Luxembourg",
        "Language": "French",
        "National reporting system SmPC": """Belgique
Agence fédérale des médicaments et des produits de santé
www.afmps.be
Division Vigilance:
Site internet : www.notifieruneffetindesirable.be
e-mail : adr@fagg-afmps.be

Luxembourg
Centre Régional de Pharmacovigilance de Nancy ou Division de la pharmacie et des médicaments de
la Direction de la santé
Site internet : www.guichet.lu/pharmacovigilance""",
        "Line 1 - Country names to be bolded - SmPC": "Belgique;Luxembourg",
        "Line 2 - SmPC": "Agence fédérale des médicaments et des produits de santé; Centre Régional de Pharmacovigilance de Nancy ou Division de la pharmacie et des médicaments",
        "Line 3 - SmPC": "www.afmps.be; la Direction de la santé",
        "Line 4 - SmPC": "Division Vigilance:; Site internet : www.guichet.lu/pharmacovigilance",
        "Line 5 - SmPC": "Site internet : www.notifieruneffetindesirable.be;",
        "Line 6 - SmPC": "e-mail : adr@fagg-afmps.be;",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.afmps.be;www.notifieruneffetindesirable.be;www.guichet.lu/pharmacovigilance",
        "Link for email - SmPC": "adr@fagg-afmps.be",
        "National reporting system PL": """Belgique
Agence fédérale des médicaments et des produits de santé
www.afmps.be
Division Vigilance:
Site internet : www.notifieruneffetindesirable.be
e-mail : adr@fagg-afmps.be

Luxembourg
Centre Régional de Pharmacovigilance de Nancy ou Division de la pharmacie et des médicaments de
la Direction de la santé
Site internet : www.guichet.lu/pharmacovigilance""",
        "Text to be appended after National reporting system PL": "En signalant les effets indésirables, vous contribuez à fournir davantage d’informations sur la sécurité du médicament.",
        "Hyperlinks PL": "www.afmps.be;www.notifieruneffetindesirable.be;www.guichet.lu/pharmacovigilance",
        "Country names to be bolded - PL": "Belgique;Luxembourg",
        "Link for email - PL": "adr@fagg-afmps.be",
        "Local Representative": """België/Belgique/Belgien
Regeneron Ireland DAC
Tél/Tel: 0800 89383

Luxembourg/Luxemburg
Regeneron Ireland DAC
Tél/Tel: 8007-9000""",
        "Country names to be bolded - Local Reps": "België/Belgique/Belgien;Luxembourg/Luxemburg",
        "Annex I Date Format": "dd month yyyy",
        "Annex IIIB Date Format": "Month yyyy",
        "Original text national reporting - SmPC": "le système national de déclaration – voir Annexe V.",
        "Text link to be deactivated": "voir Annexe V; Annexe V;www.afmps.be",
        "Annex I Date Header": "DATE DE MISE À JOUR DU TEXTE",
        "Annex IIIB Date Text": "La dernière date à laquelle cette notice a été révisée est",
        "Annex I Header in country language": "ANNEXE I",
        "Annex II Header in country language": "ANNEXE II",
        "Annex IIIB Header in country language": "B. NOTICE",
        "Original text national reporting - PL": "le système national de déclaration décrit en Annexe V.",
        "Text to be moved to the next line": "Les informations suivantes sont destinées exclusivement aux professionnels de la santé:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Belgien/Luxemburg",
        "Language": "German",
        "National reporting system SmPC": """Belgien
Föderalagentur für Arzneimittel und Gesundheitsprodukte
www.afmps.be
Abteilung Vigilanz:
Website: www.notifieruneffetindesirable.be
e-mail: adr@fagg-afmps.be

Luxemburg
Centre Régional de Pharmacovigilance de Nancy oder Abteilung Pharmazie und Medikamente
(Division de la pharmacie et des médicaments) der Gesundheitsbehörde in Luxemburg
Website : www.guichet.lu/pharmakovigilanz""",
        "Line 1 - Country names to be bolded - SmPC": "Belgien;Luxemburg",
        "Line 2 - SmPC": "Föderalagentur für Arzneimittel und Gesundheitsprodukte; Centre Régional de Pharmacovigilance de Nancy oder Abteilung Pharmazie und Medikamente",
        "Line 3 - SmPC": "www.afmps.be; (Division de la pharmacie et des médicaments) der Gesundheitsbehörde in Luxemburg",
        "Line 4 - SmPC": "Abteilung Vigilanz:;Website : www.guichet.lu/pharmakovigilanz",
        "Line 5 - SmPC": "Website: www.notifieruneffetindesirable.be;",
        "Line 6 - SmPC": "e-mail: adr@fagg-afmps.be;",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.afmps.be;www.notifieruneffetindesirable.be;www.guichet.lu/pharmakovigilanz",
        "Link for email - SmPC": "adr@fagg-afmps.be",
        "National reporting system PL": """Belgien
Föderalagentur für Arzneimittel und Gesundheitsprodukte
www.afmps.be
Abteilung Vigilanz:
Website: www.notifieruneffetindesirable.be
e-mail: adr@fagg-afmps.be

Luxemburg
Centre Régional de Pharmacovigilance de Nancy oder Abteilung Pharmazie und Medikamente
(Division de la pharmacie et des médicaments) der Gesundheitsbehörde in Luxemburg
Website : www.guichet.lu/pharmakovigilanz""",
        "Text to be appended after National reporting system PL": "Indem Sie Nebenwirkungen melden, können Sie dazu beitragen, dass mehr Informationen über die Sicherheit dieses Arzneimittels zur Verfügung gestellt werden.",
        "Hyperlinks PL": "www.afmps.be;www.notifieruneffetindesirable.be;www.guichet.lu/pharmakovigilanz",
        "Country names to be bolded - PL": "Belgien;Luxemburg",
        "Link for email - PL": "adr@fagg-afmps.be",
        "Local Representative": """België/Belgique/Belgien
Regeneron Ireland DAC
Tél/Tel: 0800 89383

Luxembourg/Luxemburg
Regeneron Ireland DAC
Tél/Tel: 8007-9000""",
        "Country names to be bolded - Local Reps": "België/Belgique/Belgien;Luxembourg/Luxemburg",
        "Annex I Date Format": "dd. MMM yyyy",
        "Annex IIIB Date Format": "MMM yyyy",
        "Original text national reporting - SmPC": "das in Anhang V aufgeführte nationale Meldesystem anzuzeigen.",
        "Text link to be deactivated": "Anhang V",
        "Annex I Date Header": "STAND DER INFORMATION",
        "Annex IIIB Date Text": "Diese Packungsbeilage wurde zuletzt überarbeitet im",
        "Annex I Header in country language": "ANHANG I",
        "Annex II Header in country language": "ANHANG II",
        "Annex IIIB Header in country language": "B. PACKUNGSBEILAGE",
        "Original text national reporting - PL": "das in Anhang V aufgeführte nationale Meldesystem anzeigen.",
        "Text to be moved to the next line": "Die folgenden Informationen sind für medizinisches Fachpersonal bestimmt:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Estonia",
        "Language": "Estonian",
        "National reporting system SmPC": """Eesti
Ravimiamet
Koduleht: www.ravimiamet.ee""",
        "Line 1 - Country names to be bolded - SmPC": "Eesti",
        "Line 2 - SmPC": "Ravimiamet",
        "Line 3 - SmPC": "Koduleht: www.ravimiamet.ee",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.ravimiamet.ee",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Eesti
Ravimiamet
Koduleht: www.ravimiamet.ee""",
        "Text to be appended after National reporting system PL": "kaudu. Teatades aitate saada rohkem infot ravimi ohutusest.",
        "Hyperlinks PL": "www.ravimiamet.ee",
        "Country names to be bolded - PL": "Eesti",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Eesti
Medison Pharma Estonia OÜ
Tel: 800 004 4845""",
        "Country names to be bolded - Local Reps": "Eesti",
        "Annex I Date Format": "dd. month yyyy",
        "Annex IIIB Date Format": "month yyyy",
        "Original text national reporting - SmPC": "riikliku teavitamissüsteemi (vt V lisa)",
        "Text link to be deactivated": "V lisa",
        "Annex I Date Header": "TEKSTI LÄBIVAATAMISE KUUPÄEV",
        "Annex IIIB Date Text": "Infoleht on viimati uuendatud",
        "Annex I Header in country language": "I LISA",
        "Annex II Header in country language": "II LISA",
        "Annex IIIB Header in country language": "B. PAKENDI INFOLEHT",
        "Original text national reporting - PL": "riikliku teavitussüsteemi (vt V lisa)",
        "Text to be moved to the next line": "Järgmine teave on ainult tervishoiutöötajatele.",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Greece/Cyprus",
        "Language": "Greek",
        "National reporting system SmPC": """Ελλάδα
Εθνικός Οργανισμός Φαρμάκων
Μεσογείων 284
GR-15562 Χολαργός, Αθήνα
Τηλ: + 30 21 32040337
Ιστότοπος: http://www.eof.gr
http://www.kitrinikarta.gr

Κύπρος
Φαρμακευτικές Υπηρεσίες
Υπουργείο Υγείας
CY-1475 Λευκωσία
Τηλ: +357 22608607
Φαξ: + 357 22608669
Ιστότοπος: www.moh.gov.cy/phs""",
        "Line 1 - Country names to be bolded - SmPC": "Ελλάδα;Κύπρος",
        "Line 2 - SmPC": "Εθνικός Οργανισμός Φαρμάκων; Φαρμακευτικές Υπηρεσίες",
        "Line 3 - SmPC": "Μεσογείων 284; Υπουργείο Υγείας",
        "Line 4 - SmPC": "GR-15562 Χολαργός; Αθήνα; CY-1475 Λευκωσία",
        "Line 5 - SmPC": "Τηλ: + 30 21 32040337; Τηλ: +357 22608607",
        "Line 6 - SmPC": "Ιστότοπος: http://www.eof.gr; Φαξ: + 357 22608669",
        "Line 7 - SmPC": "http://www.kitrinikarta.gr; Ιστότοπος: www.moh.gov.cy/phs",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "http://www.eof.gr;http://www.kitrinikarta.gr;www.moh.gov.cy/phs",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Ελλάδα
Εθνικός Οργανισμός Φαρμάκων
Μεσογείων 284
GR-15562 Χολαργός, Αθήνα
Τηλ: + 30 21 32040337
Ιστότοπος: http://www.eof.gr
http://www.kitrinikarta.gr

Κύπρος
Φαρμακευτικές Υπηρεσίες
Υπουργείο Υγείας
CY-1475 Λευκωσία
Τηλ: +357 22608607
Φαξ: + 357 22608669
Ιστότοπος: www.moh.gov.cy/phs""",
        "Text to be appended after National reporting system PL": "Μέσω της αναφοράς ανεπιθύμητων ενεργειών μπορείτε να βοηθήσετε στη συλλογή περισσότερων πληροφοριών σχετικά με την ασφάλεια του παρόντος φαρμάκου.",
        "Hyperlinks PL": "http://www.eof.gr;http://www.kitrinikarta.gr;www.moh.gov.cy/phs",
        "Country names to be bolded - PL": "Ελλάδα;Κύπρος",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Ελλάδα
ΓΕΝΕΣΙΣ ΦΑΡΜΑ Α.Ε.
Τηλ: 00800 44146336

Κύπρος
Genesis Pharma (Cyprus) Ltd
Τηλ: 800 925 47""",
        "Country names to be bolded - Local Reps": "Ελλάδα;Κύπρος",
        "Annex I Date Format": "dd Month yyyy",
        "Annex IIIB Date Format": "Month yyyy",
        "Original text national reporting - SmPC": "που αναγράφεται στο Παράρτημα V.",
        "Text link to be deactivated": "Παράρτημα V",
        "Annex I Date Header": "ΗΜΕΡΟΜΗΝΙΑ ΑΝΑΘΕΩΡΗΣΗΣ ΤΟΥ ΚΕΙΜΕΝΟΥ",
        "Annex IIIB Date Text": "Το παρόν φύλλο οδηγιών χρήσης αναθεωρήθηκε για τελευταία φορά στις",
        "Annex I Header in country language": "ΠΑΡΑΡΤΗΜΑ Ι",
        "Annex II Header in country language": "ΠΑΡΑΡΤΗΜΑ ΙΙ",
        "Annex IIIB Header in country language": "B. ΦΥΛΛΟ ΟΔΗΓΙΩΝ ΧΡΗΣΗΣ",
        "Original text national reporting - PL": "που αναγράφεται στο Παράρτημα V.",
        "Text to be moved to the next line": "Οι πληροφορίες που ακολουθούν απευθύνονται μόνο σε επαγγελματίες υγείας:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Latvia",
        "Language": "Latvian",
        "National reporting system SmPC": """Latvija
Zāļu valsts aģentūra
Jersikas iela 15
Rīga, LV 1003
Tīmekļvietne: www.zva.gov.lv""",
        "Line 1 - Country names to be bolded - SmPC": "Latvija",
        "Line 2 - SmPC": "Zāļu valsts aģentūra",
        "Line 3 - SmPC": "Jersikas iela 15",
        "Line 4 - SmPC": "Rīga, LV 1003",
        "Line 5 - SmPC": "Tīmekļvietne: www.zva.gov.lv",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.zva.gov.lv",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Latvija
Zāļu valsts aģentūra
Jersikas iela 15
Rīga, LV 1003
Tīmekļvietne: www.zva.gov.lv""",
        "Text to be appended after National reporting system PL": "Ziņojot par blakusparādībām, Jūs varat palīdzēt nodrošināt daudz plašāku informāciju par šo zāļu drošumu.",
        "Hyperlinks PL": "www.zva.gov.lv",
        "Country names to be bolded - PL": "Latvija",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Latvija
Medison Pharma Latvia SIA
Tel: 8000 5874""",
        "Country names to be bolded - Local Reps": "Latvija",
        "Annex I Date Format": "yyyy. gada dd. month",
        "Annex IIIB Date Format": "yyyy. gada month",
        "Original text national reporting - SmPC": "V pielikumā minēto nacionālās ziņošanas sistēmas kontaktinformāciju.",
        "Text link to be deactivated": "V pielikumā",
        "Annex I Date Header": "TEKSTA PĀRSKATĪŠANAS DATUMS",
        "Annex IIIB Date Text": "Šī lietošanas instrukcija pēdējo reizi pārskatīta:",
        "Annex I Header in country language": "I PIELIKUMS",
        "Annex II Header in country language": "II PIELIKUMS",
        "Annex IIIB Header in country language": "B. LIETOŠANAS INSTRUKCIJA",
        "Original text national reporting - PL": "V pielikumā minēto nacionālās ziņošanas sistēmas kontaktinformāciju.",
        "Text to be moved to the next line": "Tālāk sniegtā informācija paredzēta tikai veselības aprūpes speciālistiem.",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Lithuania",
        "Language": "Lithuanian",
        "National reporting system SmPC": """Lietuva
Valstybinė vaistų kontrolės tarnyba prie Lietuvos Respublikos sveikatos apsaugos ministerijos
Tel.: 8 800 73 568
Informacija pranešimo formos pildymui ir pateikimui: https://vvkt.lrv.lt/lt/""",
        "Line 1 - Country names to be bolded - SmPC": "Lietuva",
        "Line 2 - SmPC": "Valstybinė vaistų kontrolės tarnyba prie Lietuvos Respublikos sveikatos apsaugos ministerijos",
        "Line 3 - SmPC": "Tel.: 8 800 73 568",
        "Line 4 - SmPC": "Informacija pranešimo formos pildymui ir pateikimui: https://vvkt.lrv.lt/lt/",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "https://vvkt.lrv.lt/lt/",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Lietuva
Valstybinė vaistų kontrolės tarnyba prie Lietuvos Respublikos sveikatos apsaugos ministerijos
Tel.: 8 800 73 568
Informacija pranešimo formos pildymui ir pateikimui: https://vvkt.lrv.lt/lt/""",
        "Text to be appended after National reporting system PL": "Pranešdami apie šalutinį poveikį galite mums padėti gauti daugiau informacijos apie šio vaisto saugumą.",
        "Hyperlinks PL": "https://vvkt.lrv.lt/lt/",
        "Country names to be bolded - PL": "Lietuva",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Lietuva
Medison Pharma Lithuania UAB
Tel: 8 800 33598""",
        "Country names to be bolded - Local Reps": "Lietuva",
        "Annex I Date Format": "yyyy m. month dd d.",
        "Annex IIIB Date Format": "yyyy m. month mėn.",
        "Original text national reporting - SmPC": "V priede nurodyta nacionaline pranešimo sistema.",
        "Text link to be deactivated": "V priede",
        "Annex I Date Header": "TEKSTO PERŽIŪROS DATA",
        "Annex IIIB Date Text": "Šis pakuotės lapelis paskutinį kartą peržiūrėtas",
        "Annex I Header in country language": "I PRIEDAS",
        "Annex II Header in country language": "II PRIEDAS",
        "Annex IIIB Header in country language": "B. PAKUOTĖS LAPELIS",
        "Original text national reporting - PL": "V priede nurodyta nacionaline pranešimo sistema.",
        "Text to be moved to the next line": "Toliau pateikta informacija skirta tik sveikatos priežiūros specialistams.",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Portugal",
        "Language": "Portuguese",
        "National reporting system SmPC": """Portugal
Sítio da internet: http://www.infarmed.pt/web/infarmed/submissaoram 
(preferencialmente) 
ou através dos seguintes contactos:
Direção de Gestão do Risco de Medicamentos
Parque da Saúde de Lisboa, Av. Brasil 53
1749-004 Lisboa
Tel: +351 21 798 73 73
Linha do Medicamento: 800222444 (gratuita)
e-mail: farmacovigilancia@infarmed.pt""",
        "Line 1 - Country names to be bolded - SmPC": "Portugal",
        "Line 2 - SmPC": "Sítio da internet: http://www.infarmed.pt/web/infarmed/submissaoram",
        "Line 3 - SmPC": "(preferencialmente)",
        "Line 4 - SmPC": "ou através dos seguintes contactos:",
        "Line 5 - SmPC": "Direção de Gestão do Risco de Medicamentos",
        "Line 6 - SmPC": "Parque da Saúde de Lisboa, Av. Brasil 53",
        "Line 7 - SmPC": "1749-004 Lisboa",
        "Line 8 - SmPC": "Tel: +351 21 798 73 73",
        "Line 9 - SmPC": "Linha do Medicamento: 800222444 (gratuita)",
        "Line 10 - SmPC": "e-mail: farmacovigilancia@infarmed.pt",
        "Hyperlinks SmPC": "http://www.infarmed.pt/web/infarmed/submissaoram",
        "Link for email - SmPC": "farmacovigilancia@infarmed.pt",
        "National reporting system PL": """Portugal
Sítio da internet: http://www.infarmed.pt/web/infarmed/submissaoram 
(preferencialmente) 
ou através dos seguintes contactos:
Direção de Gestão do Risco de Medicamentos
Parque da Saúde de Lisboa, Av. Brasil 53
1749-004 Lisboa
Tel: +351 21 798 73 73
Linha do Medicamento: 800222444 (gratuita)
e-mail: farmacovigilancia@infarmed.pt""",
        "Text to be appended after National reporting system PL": "Ao comunicar efeitos indesejáveis, estará a ajudar a fornecer mais informações sobre a segurança deste medicamento.",
        "Hyperlinks PL": "http://www.infarmed.pt/web/infarmed/submissaoram",
        "Country names to be bolded - PL": "Portugal",
        "Link for email - PL": "farmacovigilancia@infarmed.pt",
        "Local Representative": """Portugal
Regeneron Ireland DAC
Tel: 800783394""",
        "Country names to be bolded - Local Reps": "Portugal",
        "Annex I Date Format": "dd de month de yyyy",
        "Annex IIIB Date Format": "em month de yyyy.",
        "Original text national reporting - SmPC": "sistema nacional de notificação mencionado no Apêndice V.",
        "Text link to be deactivated": "Apêndice V",
        "Annex I Date Header": "DATA DA REVISÃO DO TEXTO",
        "Annex IIIB Date Text": "Este folheto foi revisto pela última vez:",
        "Annex I Header in country language": "ANEXO I",
        "Annex II Header in country language": "ANEXO II",
        "Annex IIIB Header in country language": "B. FOLHETO INFORMATIVO",
        "Original text national reporting - PL": "sistema nacional de notificação mencionado no Apêndice V.",
        "Text to be moved to the next line": "A informação que se segue destina-se apenas aos profissionais de saúde:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Croatia",
        "Language": "Croatian",
        "National reporting system SmPC": """Hrvatska
Agencija za lijekove i medicinske proizvode (HALMED)
Internetska stranica: www.halmed.hr ili potražite HALMED aplikaciju putem Google Play ili Apple App Store trgovine""",
        "Line 1 - Country names to be bolded - SmPC": "Hrvatska",
        "Line 2 - SmPC": "Agencija za lijekove i medicinske proizvode (HALMED)",
        "Line 3 - SmPC": "Internetska stranica: www.halmed.hr ili potražite HALMED aplikaciju putem Google Play ili Apple App Store trgovine",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.halmed.hr",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Hrvatska
Agencija za lijekove i medicinske proizvode (HALMED)
Internetska stranica: www.halmed.hr ili potražite HALMED aplikaciju putem Google Play ili Apple App Store trgovine""",
        "Text to be appended after National reporting system PL": "Prijavljivanjem nuspojava možete pridonijeti u procjeni sigurnosti ovog lijeka.",
        "Hyperlinks PL": "www.halmed.hr",
        "Country names to be bolded - PL": "Hrvatska",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Hrvatska
Medison Pharma d.o.o.
Tel: 0800 787 074""",
        "Country names to be bolded - Local Reps": "Hrvatska",
        "Annex I Date Format": "dd. month yyyy",
        "Annex IIIB Date Format": "month yyyy.",
        "Original text national reporting - SmPC": ": navedenog u Dodatku V.",
        "Text link to be deactivated": "Dodatku V",
        "Annex I Date Header": "DATUM REVIZIJE TEKSTA",
        "Annex IIIB Date Text": "Ova uputa je zadnji puta revidirana u",
        "Annex I Header in country language": "PRILOG I.",
        "Annex II Header in country language": "PRILOG II.",
        "Annex IIIB Header in country language": "B. UPUTA O LIJEKU",
        "Original text national reporting - PL": "navedenog u Dodatku V.",
        "Text to be moved to the next line": "Sljedeće informacije namijenjene su samo zdravstvenim radnicima:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Slovenia",
        "Language": "Slovenian",
        "National reporting system SmPC": """Slovenija
Javna agencija Republike Slovenije za zdravila in medicinske pripomočke
Sektor za farmakovigilanco
Nacionalni center za farmakovigilanco
Slovenčeva ulica 22
SI-1000 Ljubljana
Tel: +386 (0)8 2000 500
Faks: +386 (0)8 2000 510
e-pošta: h-farmakovigilanca@jazmp.si
spletna stran: www.jazmp.si""",
        "Line 1 - Country names to be bolded - SmPC": "Slovenija",
        "Line 2 - SmPC": "Javna agencija Republike Slovenije za zdravila in medicinske pripomočke",
        "Line 3 - SmPC": "Sektor za farmakovigilanco",
        "Line 4 - SmPC": "Nacionalni center za farmakovigilanco",
        "Line 5 - SmPC": "Slovenčeva ulica 22",
        "Line 6 - SmPC": "SI-1000 Ljubljana",
        "Line 7 - SmPC": "Tel: +386 (0)8 2000 500",
        "Line 8 - SmPC": "Faks: +386 (0)8 2000 510",
        "Line 9 - SmPC": "e-pošta: h-farmakovigilanca@jazmp.si",
        "Line 10 - SmPC": "spletna stran: www.jazmp.si",
        "Hyperlinks SmPC": "www.jazmp.si",
        "Link for email - SmPC": "h-farmakovigilanca@jazmp.si",
        "National reporting system PL": """Slovenija
Javna agencija Republike Slovenije za zdravila in medicinske pripomočke
Sektor za farmakovigilanco
Nacionalni center za farmakovigilanco
Slovenčeva ulica 22
SI-1000 Ljubljana
Tel: +386 (0)8 2000 500
Faks: +386 (0)8 2000 510
e-pošta: h-farmakovigilanca@jazmp.si
spletna stran: www.jazmp.si""",
        "Text to be appended after National reporting system PL": "S tem, ko poročate o neželenih učinkih, lahko prispevate k zagotovitvi več informacij o varnosti tega zdravila.",
        "Hyperlinks PL": "www.jazmp.si",
        "Country names to be bolded - PL": "Slovenija",
        "Link for email - PL": "h-farmakovigilanca@jazmp.si",
        "Local Representative": """Slovenija
Medison Pharma d.o.o.
Tel: 0800 83155""",
        "Country names to be bolded - Local Reps": "Slovenija",
        "Annex I Date Format": "dd. month yyyy",
        "Annex IIIB Date Format": "month yyyy.",
        "Original text national reporting - SmPC": "nacionalni center za poročanje, ki je naveden v Prilogi V.",
        "Text link to be deactivated": "Prilogi V",
        "Annex I Date Header": "DATUM ZADNJE REVIZIJE BESEDILA",
        "Annex IIIB Date Text": "Navodilo je bilo nazadnje revidirano:",
        "Annex I Header in country language": "PRILOGA I",
        "Annex II Header in country language": "PRILOGA II",
        "Annex IIIB Header in country language": "B. NAVODILO ZA UPORABO",
        "Original text national reporting - PL": "nacionalni center za poročanje, ki je naveden v Prilogi V.",
        "Text to be moved to the next line": "Naslednje informacije so namenjene samo zdravstvenemu osebju:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Finland",
        "Language": "Finnish",
        "National reporting system SmPC": """Suomi
www-sivusto: www.fimea.fi
Lääkealan turvallisuus- ja kehittämiskeskus Fimea
Lääkkeiden haittavaikutusrekisteri
PL 55
00034 FIMEA""",
        "Line 1 - Country names to be bolded - SmPC": "Suomi",
        "Line 2 - SmPC": "www-sivusto: www.fimea.fi",
        "Line 3 - SmPC": "Lääkealan turvallisuus- ja kehittämiskeskus Fimea",
        "Line 4 - SmPC": "Lääkkeiden haittavaikutusrekisteri",
        "Line 5 - SmPC": "PL 55",
        "Line 6 - SmPC": "00034 FIMEA",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.fimea.fi",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Suomi
www-sivusto: www.fimea.fi
Lääkealan turvallisuus- ja kehittämiskeskus Fimea
Lääkkeiden haittavaikutusrekisteri
PL 55
00034 FIMEA""",
        "Text to be appended after National reporting system PL": "Ilmoittamalla haittavaikutuksista voit auttaa saamaan enemmän tietoa tämän lääkevalmisteen turvallisuudesta.",
        "Hyperlinks PL": "www.fimea.fi",
        "Country names to be bolded - PL": "Suomi",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Suomi
Regeneron Ireland DAC
Puh/Tel: 0800 772223""",
        "Country names to be bolded - Local Reps": "Suomi",
        "Annex I Date Format": "dd. month yyyy",
        "Annex IIIB Date Format": "month yyyy",
        "Original text national reporting - SmPC": "liitteessä V luetellun kansallisen ilmoitusjärjestelmän kautta.",
        "Text link to be deactivated": "liitteessä V",
        "Annex I Date Header": "TEKSTIN MUUTTAMISPÄIVÄMÄÄRÄ",
        "Annex IIIB Date Text": "Tämä pakkausseloste on tarkistettu viimeksi",
        "Annex I Header in country language": "LIITE I",
        "Annex II Header in country language": "LIITE II",
        "Annex IIIB Header in country language": "B. PAKKAUSSELOSTE",
        "Original text national reporting - PL": "liitteessä V luetellun kansallisen ilmoitusjärjestelmän kautta.",
        "Text to be moved to the next line": "Seuraavat tiedot on tarkoitettu vain terveydenhuollon ammattilaisille:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Sweden/Finland",
        "Language": "Swedish",
        "National reporting system SmPC": """Sverige
Läkemedelsverket
Box 26
751 03 Uppsala
Webbplats: www.lakemedelsverket.se

Finland
webbplats: www.fimea.fi
Säkerhets- och utvecklingscentret för läkemedelsområdet Fimea
Biverkningsregistret
PB 55
00034 FIMEA""",
        "Line 1 - Country names to be bolded - SmPC": "Sverige;Finland",
        "Line 2 - SmPC": "Läkemedelsverket; webbplats: www.fimea.fi",
        "Line 3 - SmPC": "Box 26; Säkerhets- och utvecklingscentret för läkemedelsområdet Fimea",
        "Line 4 - SmPC": "751 03 Uppsala; Biverkningsregistret",
        "Line 5 - SmPC": "Webbplats: www.lakemedelsverket.se; 00034 FIMEA",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.lakemedelsverket.se;www.fimea.fi",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Sverige
Läkemedelsverket
Box 26
751 03 Uppsala
Webbplats: www.lakemedelsverket.se

Finland
webbplats: www.fimea.fi
Säkerhets- och utvecklingscentret för läkemedelsområdet Fimea
Biverkningsregistret
PB 55
00034 FIMEA""",
        "Text to be appended after National reporting system PL": "Genom att rapportera biverkningar kan du bidra till att öka informationen om läkemedels säkerhet.",
        "Hyperlinks PL": "www.lakemedelsverket.se;www.fimea.fi",
        "Country names to be bolded - PL": "Sverige;Finland",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Sverige
Regeneron Ireland DAC
Tel: 0201 604786

Finland
Regeneron Ireland DAC
Puh/Tel: 0800 772223
""",
        "Country names to be bolded - Local Reps": "Sverige;Finland",
        "Annex I Date Format": "dd month yyyy",
        "Annex IIIB Date Format": "month yyyy.",
        "Original text national reporting - SmPC": "det nationella rapporteringssystemet listat i bilaga V.",
        "Text link to be deactivated": "bilaga V",
        "Annex I Date Header": "DATUM FÖR ÖVERSYN AV PRODUKTRESUMÉN",
        "Annex IIIB Date Text": "Denna bipacksedel ändrades senast:",
        "Annex I Header in country language": "BILAGA I",
        "Annex II Header in country language": "BILAGA II",
        "Annex IIIB Header in country language": "B. BIPACKSEDEL",
        "Original text national reporting - PL": "det nationella rapporteringssystemet listat i bilaga V.",
        "Text to be moved to the next line": "Följande uppgifter är endast avsedda för hälso- och sjukvårdspersonal:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Germany/Österreich",
        "Language": "German",
        "National reporting system SmPC": """Deutschland
Bundesinstitut für Impfstoffe und biomedizinische Arzneimittel
Paul-Ehrlich-Institut
Paul-Ehrlich-Str. 51-59
63225 Langen
Tel: +49 6103 77 0
Fax: +49 6103 77 1234
Website: www.pei.de

Österreich
Bundesamt für Sicherheit im Gesundheitswesen
Traisengasse 5
1200 WIEN
ÖSTERREICH
Fax: + 43 (0) 50 555 36207
Website: http://www.basg.gv.at/""",
        "Line 1 - Country names to be bolded - SmPC": "Deutschland;Österreich",
        "Line 2 - SmPC": "Bundesinstitut für Impfstoffe und biomedizinische Arzneimittel; Bundesamt für Sicherheit im Gesundheitswesen",
        "Line 3 - SmPC": "Paul-Ehrlich-Institut; Traisengasse 5",
        "Line 4 - SmPC": "Paul-Ehrlich-Str. 51-59; 1200 WIEN",
        "Line 5 - SmPC": "63225 Langen; ÖSTERREICH",
        "Line 6 - SmPC": "Tel: +49 6103 77 0; Fax: + 43 (0) 50 555 36207",
        "Line 7 - SmPC": "Fax: +49 6103 77 1234; Website: http://www.basg.gv.at/",
        "Line 8 - SmPC": "Website: www.pei.de;",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.pei.de;http://www.basg.gv.at/",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Deutschland
Bundesinstitut für Impfstoffe und biomedizinische Arzneimittel
Paul-Ehrlich-Institut
Paul-Ehrlich-Str. 51-59
63225 Langen
Tel: +49 6103 77 0
Fax: +49 6103 77 1234
Website: www.pei.de

Österreich
Bundesamt für Sicherheit im Gesundheitswesen
Traisengasse 5
1200 WIEN
ÖSTERREICH
Fax: + 43 (0) 50 555 36207
Website: http://www.basg.gv.at/""",
        "Text to be appended after National reporting system PL": "Indem Sie Nebenwirkungen melden, können Sie dazu beitragen, dass mehr Informationen über die Sicherheit dieses Arzneimittels zur Verfügung gestellt werden.",
        "Hyperlinks PL": "www.pei.de;http://www.basg.gv.at/",
        "Country names to be bolded - PL": "Deutschland;Österreich",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Deutschland
Regeneron GmbH
Tel.: 0800 330 4267

Österreich
Regeneron Ireland DAC
Tel: 01206094094
""",
        "Country names to be bolded - Local Reps": "Deutschland;Österreich",
        "Annex I Date Format": "dd Month yyyy",
        "Annex IIIB Date Format": "Month yyyy.",
        "Original text national reporting - SmPC": "das in Anhang V aufgeführte nationale Meldesystem anzuzeigen.",
        "Text link to be deactivated": "Anhang V",
        "Annex I Date Header": "STAND DER INFORMATION",
        "Annex IIIB Date Text": "Diese Packungsbeilage wurde zuletzt überarbeitet im",
        "Annex I Header in country language": "ANHANG I",
        "Annex II Header in country language": "ANHANG II",
        "Annex IIIB Header in country language": "B. PACKUNGSBEILAGE",
        "Original text national reporting - PL": "das in Anhang V aufgeführte nationale Meldesystem anzeigen.",
        "Text to be moved to the next line": "Die folgenden Informationen sind für medizinisches Fachpersonal bestimmt:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Italy",
        "Language": "Italian",
        "National reporting system SmPC": """Italia
Agenzia Italiana del Farmaco
Sito web: 
https://www.aifa.gov.it/content/segnalazioni-reazioni-avverse""",
        "Line 1 - Country names to be bolded - SmPC": "Italia",
        "Line 2 - SmPC": "Agenzia Italiana del Farmaco",
        "Line 3 - SmPC": "Sito web:",
        "Line 4 - SmPC": "https://www.aifa.gov.it/content/segnalazioni-reazioni-avverse",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "https://www.aifa.gov.it/content/segnalazioni-reazioni-avverse",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Italia
Agenzia Italiana del Farmaco
Sito web: 
https://www.aifa.gov.it/content/segnalazioni-reazioni-avverse""",
        "Text to be appended after National reporting system PL": "Segnalando gli effetti indesiderati può contribuire a fornire maggiori informazioni sulla sicurezza di questo medicinale.",
        "Hyperlinks PL": "https://www.aifa.gov.it/content/segnalazioni-reazioni-avverse",
        "Country names to be bolded - PL": "Italia",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Italia
Regeneron Italy S.r.l.
Tel: 800180052
""",
        "Country names to be bolded - Local Reps": "Italia",
        "Annex I Date Format": "mm/yyyy",
        "Annex IIIB Date Format": "mm/yyyy",
        "Original text national reporting - SmPC": "il sistema nazionale di segnalazione riportato nell’allegato V.",
        "Text link to be deactivated": "allegato V",
        "Annex I Date Header": "DATA DI REVISIONE DEL TESTO",
        "Annex IIIB Date Text": "Questo foglio illustrativo è stato aggiornato",
        "Annex I Header in country language": "ALLEGATO I",
        "Annex II Header in country language": "ALLEGATO II",
        "Annex IIIB Header in country language": "B. FOGLIO ILLUSTRATIVO",
        "Original text national reporting - PL": "il sistema nazionale di segnalazione riportato nell’allegato V.",
        "Text to be moved to the next line": "Le informazioni seguenti sono destinate esclusivamente agli operatori sanitari:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Spain",
        "Language": "Spanish",
        "National reporting system SmPC": """España
Sistema Español de Farmacovigilancia de Medicamentos de Uso Humano: www.notificaRAM.es""",
        "Line 1 - Country names to be bolded - SmPC": "España",
        "Line 2 - SmPC": "Sistema Español de Farmacovigilancia de Medicamentos de Uso Humano: www.notificaRAM.es",
        "Line 3 - SmPC": "",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.notificaRAM.es",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """España
Sistema Español de Farmacovigilancia de Medicamentos de Uso Humano: www.notificaRAM.es""",
        "Text to be appended after National reporting system PL": "Mediante la comunicación de efectos adversos usted puede contribuir a proporcionar más información sobre la seguridad de este medicamento.",
        "Hyperlinks PL": "www.notificaRAM.es",
        "Country names to be bolded - PL": "España",
        "Link for email - PL": "*N/A*",
        "Local Representative": """España
Regeneron Spain S.L.U.
Tel: 900031311""",
        "Country names to be bolded - Local Reps": "España",
        "Annex I Date Format": "dd Month yyyy",
        "Annex IIIB Date Format": "Month yyyy",
        "Original text national reporting - SmPC": "del sistema nacional de notificación incluido en el Apéndice V.",
        "Text link to be deactivated": "Apéndice V",
        "Annex I Date Header": "FECHA DE LA REVISIÓN DEL TEXTO",
        "Annex IIIB Date Text": "Fecha de la última revisión de este prospecto:",
        "Annex I Header in country language": "ANEXO I",
        "Annex II Header in country language": "ANEXO II",
        "Annex IIIB Header in country language": "B. PROSPECTO",
        "Original text national reporting - PL": "del sistema nacional de notificación incluido en el Apéndice V.",
        "Text to be moved to the next line": "Esta información está destinada únicamente a profesionales sanitarios:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Ireland/Malta",
        "Language": "English",
        "National reporting system SmPC": """Ireland 
HPRA Pharmacovigilance
Website: www.hpra.ie

Malta 
ADR Reporting Website: www.medicinesauthority.gov.mt/adrportal""",
        "Line 1 - Country names to be bolded - SmPC": "Ireland;Malta",
        "Line 2 - SmPC": "HPRA Pharmacovigilance; ADR Reporting Website: www.medicinesauthority.gov.mt/adrportal",
        "Line 3 - SmPC": "Website: www.hpra.ie",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.hpra.ie;www.medicinesauthority.gov.mt/adrportal",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Ireland 
HPRA Pharmacovigilance
Website: www.hpra.ie

Malta 
ADR Reporting Website: www.medicinesauthority.gov.mt/adrportal""",
        "Text to be appended after National reporting system PL": "By reporting side effects you can help provide more information on the safety of this medicine.",
        "Hyperlinks PL": "www.hpra.ie;www.medicinesauthority.gov.mt/adrportal",
        "Country names to be bolded - PL": "Ireland;Malta",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Ireland 
Regeneron Ireland DAC
Tel: 1800800920

Malta 
Genesis Pharma (Cyprus) Ltd
Tel: 80065169""",
        "Country names to be bolded - Local Reps": "Ireland;Malta",
        "Annex I Date Format": "dd Month yyyy",
        "Annex IIIB Date Format": "Month yyyy",
        "Original text national reporting - SmPC": "the national reporting system listed in Appendix V.",
        "Text link to be deactivated": "Appendix V",
        "Annex I Date Header": "DATE OF REVISION OF THE TEXT",
        "Annex IIIB Date Text": "This leaflet was last revised in",
        "Annex I Header in country language": "ANNEX I",
        "Annex II Header in country language": "ANNEX II",
        "Annex IIIB Header in country language": "B. PACKAGE LEAFLET",
        "Original text national reporting - PL": "the national reporting system listed in Appendix V.",
        "Text to be moved to the next line": "The following information is intended for healthcare professionals only:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Malta",
        "Language": "Maltese",
        "National reporting system SmPC": """Malta
ADR Reporting Website: www.medicinesauthority.gov.mt/adrportal""",
        "Line 1 - Country names to be bolded - SmPC": "Malta",
        "Line 2 - SmPC": "ADR Reporting Website: www.medicinesauthority.gov.mt/adrportal",
        "Line 3 - SmPC": "",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.medicinesauthority.gov.mt/adrportal",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Malta
ADR Reporting Website: www.medicinesauthority.gov.mt/adrportal""",
        "Text to be appended after National reporting system PL": "Billi tirrapporta l-effetti sekondarji tista’ tgħin biex tiġi pprovduta aktar informazzjoni dwar is-sigurtà ta’ din il-mediċina.",
        "Hyperlinks PL": "www.medicinesauthority.gov.mt/adrportal",
        "Country names to be bolded - PL": "Malta",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Malta
Genesis Pharma (Cyprus) Ltd
Tel: 80065169 
""",
        "Country names to be bolded - Local Reps": "Malta",
        "Annex I Date Format": "dd month yyyy",
        "Annex IIIB Date Format": "month yyyy",
        "Original text national reporting - SmPC": "tas-sistema ta’ rappurtar nazzjonali imniżżla f’Appendiċi V.",
        "Text link to be deactivated": "Appendiċi V",
        "Annex I Date Header": "DATA TA’ REVIŻJONI TAT-TEST",
        "Annex IIIB Date Text": "Dan il-fuljett kien rivedut l-aħħar f’:",
        "Annex I Header in country language": "ANNESS I",
        "Annex II Header in country language": "ANNESS II",
        "Annex IIIB Header in country language": "B. FULJETT TA’ TAGĦRIF",
        "Original text national reporting - PL": "tas-sistema ta’ rappurtar nazzjonali mniżżla f’Appendiċi V.",
        "Text to be moved to the next line": "It-tagħrif li jmiss qed jingħata biss għall-professjonisti tal-kura tas-saħħa biss:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "France",
        "Language": "French",
        "National reporting system SmPC": """France
Agence nationale de sécurité du médicament et des produits de santé (ANSM)
et réseau des Centres Régionaux de Pharmacovigilance 
Site internet: https://signalement.social-sante.gouv.fr/""",
        "Line 1 - Country names to be bolded - SmPC": "France",
        "Line 2 - SmPC": "Agence nationale de sécurité du médicament et des produits de santé (ANSM)",
        "Line 3 - SmPC": "et réseau des Centres Régionaux de Pharmacovigilance",
        "Line 4 - SmPC": "Site internet: https://signalement.social-sante.gouv.fr/",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "https://signalement.social-sante.gouv.fr/",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """France
Agence nationale de sécurité du médicament et des produits de santé (ANSM)
et réseau des Centres Régionaux de Pharmacovigilance 
Site internet: https://signalement.social-sante.gouv.fr/""",
        "Text to be appended after National reporting system PL": "En signalant les effets indésirables, vous contribuez à fournir davantage d’informations sur la sécurité du médicament.",
        "Hyperlinks PL": "https://signalement.social-sante.gouv.fr/",
        "Country names to be bolded - PL": "France",
        "Link for email - PL": "*N/A*",
        "Local Representative": """France
Regeneron France SAS
Tél: 080 554 3951
""",
        "Country names to be bolded - Local Reps": "France",
        "Annex I Date Format": "dd Month yyyy",
        "Annex IIIB Date Format": "Month yyyy",
        "Original text national reporting - SmPC": "le système national de déclaration – voir Annexe V.",
        "Text link to be deactivated": "Annexe V",
        "Annex I Date Header": "DATE DE MISE À JOUR DU TEXTE",
        "Annex IIIB Date Text": "La dernière date à laquelle cette notice a été révisée est",
        "Annex I Header in country language": "ANNEXE I",
        "Annex II Header in country language": "ANNEXE II",
        "Annex IIIB Header in country language": "B. NOTICE",
        "Original text national reporting - PL": "le système national de déclaration décrit en Annexe V.",
        "Text to be moved to the next line": "Les informations suivantes sont destinées exclusivement aux professionnels de la santé:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Denmark",
        "Language": "Danish",
        "National reporting system SmPC": """Danmark
Lægemiddelstyrelsen
Axel Heides Gade 1
DK-2300 København S
Websted: www.meldenbivirkning.dk""",
        "Line 1 - Country names to be bolded - SmPC": "Danmark",
        "Line 2 - SmPC": "Lægemiddelstyrelsen",
        "Line 3 - SmPC": "Axel Heides Gade 1",
        "Line 4 - SmPC": "DK-2300 København S",
        "Line 5 - SmPC": "Websted: www.meldenbivirkning.dk",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.meldenbivirkning.dk",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Danmark
Lægemiddelstyrelsen
Axel Heides Gade 1
DK-2300 København S
Websted: www.meldenbivirkning.dk""",
        "Text to be appended after National reporting system PL": "Ved at indrapportere bivirkninger kan du hjælpe med at fremskaffe mere information om sikkerheden af dette lægemiddel.",
        "Hyperlinks PL": "www.meldenbivirkning.dk",
        "Country names to be bolded - PL": "Danmark",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Danmark
Regeneron Ireland DAC
Tlf: 80 20 03 57
""",
        "Country names to be bolded - Local Reps": "Danmark",
        "Annex I Date Format": "mm/yyyy",
        "Annex IIIB Date Format": "month yyyy",
        "Original text national reporting - SmPC": "det nationale rapporteringssystem anført i Appendiks V.",
        "Text link to be deactivated": "Appendiks V",
        "Annex I Date Header": "DATO FOR ÆNDRING AF TEKSTEN",
        "Annex IIIB Date Text": "Denne indlægsseddel blev senest ændret",
        "Annex I Header in country language": "BILAG I",
        "Annex II Header in country language": "BILAG II",
        "Annex IIIB Header in country language": "B. INDLÆGSSEDDEL",
        "Original text national reporting - PL": "det nationale rapporteringssystem anført i Appendiks V.",
        "Text to be moved to the next line": "Nedenstående oplysninger er kun til sundhedspersoner:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Iceland",
        "Language": "Icelandic",
        "National reporting system SmPC": """Ísland
til Lyfjastofnunar, www.lyfjastofnun.is""",
        "Line 1 - Country names to be bolded - SmPC": "Ísland",
        "Line 2 - SmPC": "til Lyfjastofnunar, www.lyfjastofnun.is",
        "Line 3 - SmPC": "",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.lyfjastofnun.is",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Ísland
til Lyfjastofnunar, www.lyfjastofnun.is""",
        "Text to be appended after National reporting system PL": "Með því að tilkynna aukaverkanir er hægt að hjálpa til við að auka upplýsingar um öryggi lyfsins.",
        "Hyperlinks PL": "www.lyfjastofnun.is",
        "Country names to be bolded - PL": "Ísland",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Ísland
Regeneron Ireland DAC
Sími: 800 4431
""",
        "Country names to be bolded - Local Reps": "Ísland",
        "Annex I Date Format": "mm/yyyy",
        "Annex IIIB Date Format": "month yyyy",
        "Original text national reporting - SmPC": "samkvæmt fyrirkomulagi sem gildir í hverju landi fyrir sig, sjá Appendix V.",
        "Text link to be deactivated": "Appendix V",
        "Annex I Date Header": "DAGSETNING ENDURSKOÐUNAR TEXTANS",
        "Annex IIIB Date Text": "Þessi fylgiseðill var síðast uppfærður í",
        "Annex I Header in country language": "VIÐAUKI I",
        "Annex II Header in country language": "VIÐAUKI II",
        "Annex IIIB Header in country language": "B. FYLGISEÐILL",
        "Original text national reporting - PL": "samkvæmt fyrirkomulagi sem gildir í hverju landi fyrir sig, sjá Appendix V.",
        "Text to be moved to the next line": "Eftirfarandi upplýsingar eru einungis ætlaðar heilbrigðisstarfsmönnum:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Norway",
        "Language": "Norwegian",
        "National reporting system SmPC": """Norge
Direktoratet for medisinske produkter
Nettside: www.dmp.no/meldeskjema""",
        "Line 1 - Country names to be bolded - SmPC": "Norge",
        "Line 2 - SmPC": "Direktoratet for medisinske produkter",
        "Line 3 - SmPC": "Nettside: www.dmp.no/meldeskjema",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "",
        "Line 6 - SmPC": "",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.dmp.no/meldeskjema",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Norge
Direktoratet for medisinske produkter
Nettside: www.dmp.no/pasientmelding""",
        "Text to be appended after National reporting system PL": "Ved å melde fra om bivirkninger bidrar du med informasjon om sikkerheten ved bruk av dette legemidlet.",
        "Hyperlinks PL": "www.dmp.no/pasientmelding",
        "Country names to be bolded - PL": "Norge",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Norge
Regeneron Ireland DAC
Tlf: 8003 15 33
""",
        "Country names to be bolded - Local Reps": "Norge",
        "Annex I Date Format": "MM/YYYY",
        "Annex IIIB Date Format": "month yyyy",
        "Original text national reporting - SmPC": "det nasjonale meldesystemet som beskrevet i Appendix V.",
        "Text link to be deactivated": "Appendix V",
        "Annex I Date Header": "OPPDATERINGSDATO",
        "Annex IIIB Date Text": "Dette pakningsvedlegget ble sist oppdatert",
        "Annex I Header in country language": "VEDLEGG I",
        "Annex II Header in country language": "VEDLEGG II",
        "Annex IIIB Header in country language": "B. PAKNINGSVEDLEGG",
        "Original text national reporting - PL": "det nasjonale meldesystemet som beskrevet i Appendix V.",
        "Text to be moved to the next line": "Påfølgende informasjon er bare beregnet på helsepersonell:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Czech Republic",
        "Language": "Czech",
        "National reporting system SmPC": """Česká republika
webového formuláře 
www.sukl.gov.cz/nezadouciucinky

případně na adresu:
Státní ústav pro kontrolu léčiv
Šrobárova 49/48
100 00 Praha 10
email: farmakovigilance@sukl.gov.cz """,
        "Line 1 - Country names to be bolded - SmPC": "Česká republika",
        "Line 2 - SmPC": "webového formuláře",
        "Line 3 - SmPC": "www.sukl.gov.cz/nezadouciucinky",
        "Line 4 - SmPC": "",
        "Line 5 - SmPC": "případně na adresu:",
        "Line 6 - SmPC": "Státní ústav pro kontrolu léčiv",
        "Line 7 - SmPC": "Šrobárova 49/48",
        "Line 8 - SmPC": "100 00 Praha 10",
        "Line 9 - SmPC": "email: farmakovigilance@sukl.gov.cz",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.sukl.gov.cz/nezadouciucinky",
        "Link for email - SmPC": "farmakovigilance@sukl.gov.cz",
        "National reporting system PL": """Česká republika
webového formuláře 
www.sukl.gov.cz/nezadouciucinky

případně na adresu:
Státní ústav pro kontrolu léčiv
Šrobárova 49/48
100 00 Praha 10
email: farmakovigilance@sukl.gov.cz """,
        "Text to be appended after National reporting system PL": "Nahlášením nežádoucích účinků můžete přispět k získání více informací o bezpečnosti tohoto přípravku.",
        "Hyperlinks PL": "www.sukl.gov.cz/nezadouciucinky",
        "Country names to be bolded - PL": "Česká republika",
        "Link for email - PL": "farmakovigilance@sukl.gov.cz",
        "Local Representative": """Česká republika
Medison Pharma s.r.o.
Tel: 800 050 148
""",
        "Country names to be bolded - Local Reps": "Česká republika",
        "Annex I Date Format": "dd. month yyyy",
        "Annex IIIB Date Format": "mm/yyyy",
        "Original text national reporting - SmPC": "národního systému hlášení nežádoucích účinků uvedeného v Dodatku V.",
        "Text link to be deactivated": "Dodatku V",
        "Annex I Date Header": "DATUM REVIZE TEXTU",
        "Annex IIIB Date Text": "Tato příbalová informace byla naposledy revidována",
        "Annex I Header in country language": "PŘÍLOHA I",
        "Annex II Header in country language": "PŘÍLOHA II",
        "Annex IIIB Header in country language": "B. PŘÍBALOVÁ INFORMACE",
        "Original text national reporting - PL": "národního systému hlášení nežádoucích účinků uvedeného v Dodatku V.",
        "Text to be moved to the next line": "Následující informace jsou určeny pouze pro zdravotnické pracovníky:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Poland",
        "Language": "Polish",
        "National reporting system SmPC": """Polska
Departament Monitorowania Niepożądanych Działań Produktów Leczniczych Urzędu Rejestracji Produktów Leczniczych, Wyrobów Medycznych i Produktów Biobójczych
Al. Jerozolimskie 181C 
PL-02 222 Warszawa
Tel.: + 48 22 49 21 301
Faks: + 48 22 49 21 309
Strona internetowa: https://smz.ezdrowie.gov.pl""",
        "Line 1 - Country names to be bolded - SmPC": "Polska",
        "Line 2 - SmPC": "Departament Monitorowania Niepożądanych Działań Produktów Leczniczych Urzędu Rejestracji Produktów Leczniczych,",
        "Line 3 - SmPC": "Wyrobów Medycznych i Produktów Biobójczych",
        "Line 4 - SmPC": "Al. Jerozolimskie 181C",
        "Line 5 - SmPC": "PL-02 222 Warszawa",
        "Line 6 - SmPC": "Tel.: + 48 22 49 21 301",
        "Line 7 - SmPC": "Faks: + 48 22 49 21 309",
        "Line 8 - SmPC": "Strona internetowa: https://smz.ezdrowie.gov.pl",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "https://smz.ezdrowie.gov.pl",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """Polska
Departament Monitorowania Niepożądanych Działań Produktów Leczniczych Urzędu Rejestracji Produktów Leczniczych, Wyrobów Medycznych i Produktów Biobójczych
Al. Jerozolimskie 181C 
PL-02 222 Warszawa
Tel.: + 48 22 49 21 301
Faks: + 48 22 49 21 309
Strona internetowa: https://smz.ezdrowie.gov.pl""",
        "Text to be appended after National reporting system PL": "Dzięki zgłaszaniu działań niepożądanych można będzie zgromadzić więcej informacji na temat bezpieczeństwa stosowania leku.",
        "Hyperlinks PL": "https://smz.ezdrowie.gov.pl",
        "Country names to be bolded - PL": "Polska",
        "Link for email - PL": "*N/A*",
        "Local Representative": """Polska
Medison Pharma Sp. z o.o.
Tel.: 800 080 691
""",
        "Country names to be bolded - Local Reps": "Polska",
        "Annex I Date Format": "mm/yyyy",
        "Annex IIIB Date Format": "month yyyy r.",
        "Original text national reporting - SmPC": "krajowego systemu zgłaszania wymienionego w załączniku V.",
        "Text link to be deactivated": "załączniku V",
        "Annex I Date Header": "DATA ZATWIERDZENIA LUB CZĘŚCIOWEJ ZMIANY TEKSTU CHARAKTERYSTYKI PRODUKTU LECZNICZEGO",
        "Annex IIIB Date Text": "Data ostatniej aktualizacji ulotki:",
        "Annex I Header in country language": "ANEKS I",
        "Annex II Header in country language": "ANEKS II",
        "Annex IIIB Header in country language": "B. ULOTKA DLA PACJENTA",
        "Original text national reporting - PL": "„krajowego systemu zgłaszania” wymienionego w załączniku V.",
        "Text to be moved to the next line": "Informacje przeznaczone wyłącznie dla fachowego personelu medycznego:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Slovakia",
        "Language": "Slovak",
        "National reporting system SmPC": """Slovenská republika
Štátny ústav pre kontrolu liečiv
Sekcia klinického skúšania liekov a farmakovigilancie
Kvetná 11
SK-825 08 Bratislava
Tel: + 421 2 507 01 206
e-mail: neziaduce.ucinky@sukl.sk
Tlačivo na hlásenie podozrenia na nežiaduci účinok lieku je na webovej stránke www.sukl.sk v časti Bezpečnosť liekov/Hlásenie podozrení na nežiaduce účinky liekov
Formulár na elektronické podávanie hlásení: https://portal.sukl.sk/eskadra/""",
        "Line 1 - Country names to be bolded - SmPC": "Slovenská republika",
        "Line 2 - SmPC": "Štátny ústav pre kontrolu liečiv",
        "Line 3 - SmPC": "Sekcia klinického skúšania liekov a farmakovigilancie",
        "Line 4 - SmPC": "Kvetná 11",
        "Line 5 - SmPC": "SK-825 08 Bratislava",
        "Line 6 - SmPC": "Tel: + 421 2 507 01 206",
        "Line 7 - SmPC": "e-mail: neziaduce.ucinky@sukl.sk",
        "Line 8 - SmPC": "Tlačivo na hlásenie podozrenia na nežiaduci účinok lieku je na webovej stránke www.sukl.sk v časti Bezpečnosť liekov/Hlásenie podozrení na nežiaduce účinky liekov",
        "Line 9 - SmPC": "Formulár na elektronické podávanie hlásení: https://portal.sukl.sk/eskadra/",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.sukl.sk;https://portal.sukl.sk/eskadra/",
        "Link for email - SmPC": "neziaduce.ucinky@sukl.sk",
        "National reporting system PL": """Slovenská republika
Štátny ústav pre kontrolu liečiv
Sekcia klinického skúšania liekov a farmakovigilancie
Kvetná 11
SK-825 08 Bratislava
Tel: + 421 2 507 01 206
e-mail: neziaduce.ucinky@sukl.sk
Tlačivo na hlásenie podozrenia na nežiaduci účinok lieku je na webovej stránke www.sukl.sk v časti Bezpečnosť liekov/Hlásenie podozrení na nežiaduce účinky liekov
Formulár na elektronické podávanie hlásení: https://portal.sukl.sk/eskadra/""",
        "Text to be appended after National reporting system PL": "Hlásením vedľajších účinkov môžete prispieť k získaniu ďalších informácií o bezpečnosti tohto lieku.",
        "Hyperlinks PL": "www.sukl.sk;https://portal.sukl.sk/eskadra/",
        "Country names to be bolded - PL": "Slovenská republika",
        "Link for email - PL": "neziaduce.ucinky@sukl.sk",
        "Local Representative": """Slovenská republika
Medison Pharma s.r.o.
Tel.: 0800 123 255
""",
        "Country names to be bolded - Local Reps": "Slovenská republika",
        "Annex I Date Format": "mm/yyyy",
        "Annex IIIB Date Format": "mm/yyyy",
        "Original text national reporting - SmPC": "národné centrum hlásenia uvedené v Prílohe V.",
        "Text link to be deactivated": "Prílohe V",
        "Annex I Date Header": "DÁTUM REVÍZIE TEXTU",
        "Annex IIIB Date Text": "Táto písomná informácia bola naposledy aktualizovaná v",
        "Annex I Header in country language": "PRÍLOHA I",
        "Annex II Header in country language": "PRÍLOHA II",
        "Annex IIIB Header in country language": "B. PÍSOMNÁ INFORMÁCIA PRE POUŽÍVATEĽA",
        "Original text national reporting - PL": "národné centrum hlásenia uvedené v Prílohe V.",
        "Text to be moved to the next line": "Nasledujúca informácia je určená len pre zdravotníckych pracovníkov:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Bulgaria",
        "Language": "Bulgarian",
        "National reporting system SmPC": """България
Изпълнителна агенция по лекарствата
ул. „Дамян Груев“ № 8 
1303 София 
Teл.: +359 2 8903417
уебсайт: www.bda.bg""",
        "Line 1 - Country names to be bolded - SmPC": "България",
        "Line 2 - SmPC": "Изпълнителна агенция по лекарствата",
        "Line 3 - SmPC": "ул. „Дамян Груев“ № 8",
        "Line 4 - SmPC": "1303 София",
        "Line 5 - SmPC": "Teл.: +359 2 8903417",
        "Line 6 - SmPC": "уебсайт: www.bda.bg",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.bda.bg",
        "Link for email - SmPC": "*N/A*",
        "National reporting system PL": """България
Изпълнителна агенция по лекарствата
ул. „Дамян Груев“ № 8 
1303 София 
Teл.: +359 2 8903417
уебсайт: www.bda.bg""",
        "Text to be appended after National reporting system PL": "Като съобщавате нежелани реакции, можете да дадете своя принос за получаване на повече информация относно безопасността на това лекарство.",
        "Hyperlinks PL": "www.bda.bg",
        "Country names to be bolded - PL": "България",
        "Link for email - PL": "*N/A*",
        "Local Representative": """България
Medison Pharma Bulgaria Ltd.
Тел.: 008002100419
""",
        "Country names to be bolded - Local Reps": "България",
        "Annex I Date Format": "mm/yyyy",
        "Annex IIIB Date Format": "month yyyy r.",
        "Original text national reporting - SmPC": "национална система за съобщаване, посочена в Приложение V.",
        "Text link to be deactivated": "Приложение V",
        "Annex I Date Header": "ДАТА НА АКТУАЛИЗИРАНЕ НА ТЕКСТА",
        "Annex IIIB Date Text": "Дата на последно преразглеждане на листовката",
        "Annex I Header in country language": "ПРИЛОЖЕНИЕ I",
        "Annex II Header in country language": "ПРИЛОЖЕНИЕ II",
        "Annex IIIB Header in country language": "Б. ЛИСТОВКА",
        "Original text national reporting - PL": "националната система за съобщаване, посочена в Приложение V.",
        "Text to be moved to the next line": "Посочената по-долу информация е предназначена само за медицински специалисти:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Hungary",
        "Language": "Hungarian",
        "National reporting system SmPC": """Magyarország
Nemzeti Népegészségügyi és
Gyógyszerészeti Központ
Postafiók 450
H-1372 Budapest
Honlap: www.ogyei.gov.hu
elektronikus bejelentő nyomtatvány: https://mellekhatas.ogyei.gov.hu/
e-mail: adr.box@ogyei.gov.hu""",
        "Line 1 - Country names to be bolded - SmPC": "Magyarország",
        "Line 2 - SmPC": "Nemzeti Népegészségügyi és",
        "Line 3 - SmPC": "Gyógyszerészeti Központ",
        "Line 4 - SmPC": "Postafiók 450",
        "Line 5 - SmPC": "H-1372 Budapest",
        "Line 6 - SmPC": "Honlap: www.ogyei.gov.hu",
        "Line 7 - SmPC": "elektronikus bejelentő nyomtatvány: https://mellekhatas.ogyei.gov.hu/",
        "Line 8 - SmPC": "e-mail: adr.box@ogyei.gov.hu",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.ogyei.gov.hu;https://mellekhatas.ogyei.gov.hu/",
        "Link for email - SmPC": "adr.box@ogyei.gov.hu",
        "National reporting system PL": """Magyarország
Nemzeti Népegészségügyi és
Gyógyszerészeti Központ
Postafiók 450
H-1372 Budapest
Honlap: www.ogyei.gov.hu
elektronikus bejelentő nyomtatvány: https://mellekhatas.ogyei.gov.hu/
e-mail: adr.box@ogyei.gov.hu""",
        "Text to be appended after National reporting system PL": "A mellékhatások bejelentésével Ön is hozzájárulhat ahhoz, hogy minél több információ álljon rendelkezésre a gyógyszer biztonságos alkalmazásával kapcsolatban.",
        "Hyperlinks PL": "www.ogyei.gov.hu;https://mellekhatas.ogyei.gov.hu/",
        "Country names to be bolded - PL": "Magyarország",
        "Link for email - PL": "adr.box@ogyei.gov.hu",
        "Local Representative": """Magyarország
Medison Pharma Hungary Kft
Tel.: 06-809-93029
""",
        "Country names to be bolded - Local Reps": "Magyarország",
        "Annex I Date Format": "yyyy. month",
        "Annex IIIB Date Format": "yyyy. month.",
        "Original text national reporting - SmPC": "V. függelékben található elérhetőségek valamelyikén keresztül.",
        "Text link to be deactivated": "V. függelékben",
        "Annex I Date Header": "A SZÖVEG ELLENŐRZÉSÉNEK DÁTUMA",
        "Annex IIIB Date Text": "A betegtájékoztató legutóbbi felülvizsgálatának dátuma:",
        "Annex I Header in country language": "I. MELLÉKLET",
        "Annex II Header in country language": "II. MELLÉKLET",
        "Annex IIIB Header in country language": "B. BETEGTÁJÉKOZTATÓ",
        "Original text national reporting - PL": "V. függelékben található elérhetőségeken keresztül.",
        "Text to be moved to the next line": "Az alábbi információk kizárólag egészségügyi szakembereknek szólnak:",
        "Country Group": "",
        "Product": "",
    },
    {
        "Country": "Romania",
        "Language": "Romanian",
        "National reporting system SmPC": """România
Agenţia Naţională a Medicamentului şi a Dispozitivelor Medicale din România
Str. Aviator Sănătescu nr. 48, sector 1
Bucureşti 011478- RO 
e-mail: adr@anm.ro
Website: www.anm.ro""",
        "Line 1 - Country names to be bolded - SmPC": "România",
        "Line 2 - SmPC": "Agenţia Naţională a Medicamentului şi a Dispozitivelor Medicale din România",
        "Line 3 - SmPC": "Str. Aviator Sănătescu nr. 48, sector 1",
        "Line 4 - SmPC": "Bucureşti 011478- RO",
        "Line 5 - SmPC": "e-mail: adr@anm.ro",
        "Line 6 - SmPC": "Website: www.anm.ro",
        "Line 7 - SmPC": "",
        "Line 8 - SmPC": "",
        "Line 9 - SmPC": "",
        "Line 10 - SmPC": "",
        "Hyperlinks SmPC": "www.anm.ro",
        "Link for email - SmPC": "adr@anm.ro",
        "National reporting system PL": """România
Agenţia Naţională a Medicamentului şi a Dispozitivelor Medicale din România
Str. Aviator Sănătescu nr. 48, sector 1
Bucureşti 011478- RO 
e-mail: adr@anm.ro
Website: www.anm.ro""",
        "Text to be appended after National reporting system PL": "Raportând reacțiile adverse, puteți contribui la furnizarea de informații suplimentare privind siguranța acestui medicament.",
        "Hyperlinks PL": "www.anm.ro",
        "Country names to be bolded - PL": "România",
        "Link for email - PL": "adr@anm.ro",
        "Local Representative": """România
Medison Pharma SRL
Tel: 0800 400670
""",
        "Country names to be bolded - Local Reps": "România",
        "Annex I Date Format": "mm/yyyy",
        "Annex IIIB Date Format": "month yyyy.",
        "Original text national reporting - SmPC": "sistemului național de raportare, astfel cum este menționat în Anexa V.",
        "Text link to be deactivated": "Anexa V",
        "Annex I Date Header": "DATA REVIZUIRII TEXTULUI",
        "Annex IIIB Date Text": "Acest prospect a fost revizuit în:",
        "Annex I Header in country language": "ANEXA I",
        "Annex II Header in country language": "ANEXA II",
        "Annex IIIB Header in country language": "B. PROSPECTUL",
        "Original text national reporting - PL": "sistemului național de raportare, așa cum este menționat în Anexa V.",
        "Text to be moved to the next line": "Următoarele informații sunt destinate numai profesioniștilor din domeniul sănătății:",
        "Country Group": "",
        "Product": "",
    },
]


def load_default_mapping_dataframe() -> pd.DataFrame:
    """Return the default mapping table as a DataFrame."""

    return pd.DataFrame(DEFAULT_MAPPING_ROWS, columns=COLUMN_NAMES)


__all__ = [
    "COLUMN_NAMES",
    "DEFAULT_MAPPING_ROWS",
    "load_default_mapping_dataframe",
]
