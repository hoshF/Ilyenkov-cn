---
title: "Spinoza Source Notes"
created: "2026-06-11"
type: "analysis"
tags: ["source-metadata", "audit"]
language: "en"
collection: "corpus-metadata"
llm_wiki_eligible: "true"
gbrain_source: "project-markdown"
---
# Spinoza Source Notes

Generated sources and scripts were first assembled on 2026-06-09 UTC.

## Corpus Policy

The strict core identifies the language in which Spinoza composed each text. The broader LLM wiki includes both authorial-language texts and auditable contemporary or early translations and textual witnesses. Modern translations are not part of the default source corpus. Every indirect witness or translation is marked by `text_role`, `original_language_status`, `core_corpus_eligible`, and `llm_wiki_eligible` metadata.

The Dutch `Nagelate schriften`, the surviving Dutch `Korte Verhandeling`, and the current correspondence collection are all eligible for the LLM wiki because they are historically attested source texts. They remain outside the strict authorial-language core where their status differs or is unresolved.

## Latin Wikisource

The Latin Wikisource author page is used as the manifest source:

<https://la.wikisource.org/wiki/Scriptor:Benedictus_de_Spinoza>

The author page currently lists nine works. Four have usable source pages and were converted:

- `Ethica`
- `Tractatus de intellectus emendatione, et de via qua optime in veram rerum cognitionem dirigitur`
- `Tractatus Politicus`
- `Epistolae (Benedictus de Spinoza)`

Five listed works are retained in the manifest but currently resolve as missing source pages through the MediaWiki API:

- `Renati Descartes principia philosophiae more geometrico demonstrata`
- `Cogitata metaphysica`
- `Tractatus theologico-politicus`
- `Compendium Grammatices Linguae Hebraeae`
- `Ultimi barbarorum`

Those entries are marked `missing_source_page` in `spinoza_wikisource_state.json` rather than silently mapped to uncertain substitute pages.

## Ethica Structure

The `Ethica` page itself is a table of contents. The converter discovers and merges the five child pages:

- `Ethica/Pars prima - De Deo`
- `Ethica/Pars secunda - De natura et origine mentis`
- `Ethica/Pars tertia - De origine et natura affectuum`
- `Ethica/Pars quarta - De servitute humana seu de affectuum viribus`
- `Ethica/Pars quinta - De potentia intellectus seu de libertate humana`

`ethica-structured.md` and `ethica_elements.json` are generated from the merged Markdown. Element IDs follow the local convention `E1D1`, `E1A1`, `E1P1`, `E1P1Dem`, `E1P1Cor`, `E1P1Schol`, and `E1App`.

## DBNL

The Dutch `Nagelate schriften` source is fetched from DBNL TEI XML:

<https://www.dbnl.org/nieuws/xml.php?id=spin003nage01>

The DBNL downloads page is:

<https://www.dbnl.org/tekst/spin003nage01_01/downloads.php>

The generated Markdown keeps page markers such as `{==*2r==}` from the TEI `<pb>` elements.

## Dutch Wikisource Short Treatise

The surviving Dutch `Korte Verhandeling van God, de mensch en deszelvs welstand` is fetched from Dutch Wikisource:

<https://nl.wikisource.org/wiki/Korte_Verhandeling_van_God%2C_de_mensch_en_deszelvs_welstand>

The transcription links to the public-domain manuscript held by the Koninklijke Bibliotheek in The Hague as KB 75 G 15. The generated Markdown preserves the two-part structure, chapters I-X and I-XXVI, paragraph identifiers, manuscript folio markers, and the additional textual material supplied by the source page.

This Dutch text is generally considered a translation of a lost Latin original. It is the earliest surviving textual witness, but it is not described here as a securely established authorial-language original.

## Known V1 Limits

- Wikisource notes are preserved as rendered reference text, but note anchors are not yet normalized into Markdown footnote IDs.
- DBNL marginal notes are preserved inline rather than modeled as separate note objects.
- The audit records critical-edition and scan sources but does not perform automated collation against them.
- Web transcriptions are suitable for search and LLM ingestion but remain unverified against a critical edition.

## Preferred Spinoza et Nous Web Layer

Spinoza et Nous is the preferred Latin Markdown source because its MediaWiki pages provide substantially broader coverage than Latin Wikisource and can be tracked by revision ID.

Generated works:

- `Tractatus theologico-politicus` (Praefatio and Caput I-XX)
- `Renati Descartes principia philosophiae` (Praefatio and Pars I-III)
- `Cogitata metaphysica`
- `Tractatus de intellectus emendatione`
- `Ethica` (Pars I-V)
- `Tractatus politicus` (eleven chapters and `Reliqua desiderantur`)
- `Epistolae`, as a combined file and individual letter files

The files live under `spinoza_md/latin_web/spinozaetnous/`. `preferred_sources.json` records this layer as the LLM wiki default while preserving Latin Wikisource as an independent backup.

The letter source currently covers 78 regular numbered letters plus `12 bis` and `67 bis`. Numbers 38, 42, 43, 49, 69, and 84 are absent from the source and the collection is therefore marked `partial_web_transcription`.

Spinoza et Nous requires attribution and restricts use to non-commercial purposes. The generated files retain the source URL, revision IDs, site name, and license notice. This repository uses them for public, non-commercial research.

## Compendium Gap

No corresponding Spinoza et Nous web transcription has been found for `Compendium Grammatices Linguae Hebraeae`. It has no generated Markdown and is marked:

`source_pdf_available_web_transcription_missing`

The Herzog August Bibliothek also provides a TEI structure file for a 1677 `Opera Posthuma` copy:

<https://diglib.hab.de/drucke/ac-343/tei-struct.xml>

It identifies the preface and chapters I-XXXIII and links them to page scans, but it does not contain running-text transcription. The Bruder 1846 volume III PDF remains available for manual checking only. No OCR or image-derived text is substituted for the missing web transcription.

## Correspondence Gaps

The preferred Spinoza et Nous layer lacks Gebhardt numbers 38, 42, 43, 49, 69, and 84. Spinoza Web supplies manuscript/edition metadata and page-level source references for these items, but it does not provide plain-text transcriptions. Some individual texts occur in other editions or image sources; they are not merged until a non-OCR, original-language transcription can be verified consistently.

## Ultimi Barbarorum

`Ultimi barbarorum` is known from biographical testimony as the wording of a placard Spinoza reportedly intended to display after the murder of the De Witt brothers. No placard or independent manuscript survives. It is recorded as `reported_lost_fragment_no_surviving_document`, not generated as an original-text Markdown work.

## Bruder Reference Scans

All three public-domain Bruder edition PDFs are retained under `source_pdfs/`. They are reference scans only; the repository no longer generates OCR Markdown from them.

- Volume I (1843): `Renati Descartes principia philosophiae`, `Cogitata metaphysica`, and `Ethica`.
- Volume II (1844): `Tractatus de intellectus emendatione`, `Tractatus politicus`, and `Epistolae`.
- Volume III (1846): `Tractatus theologico-politicus` and `Compendium grammatices linguae Hebraeae`.

Source pages:

- Volume I: <https://rcin.org.pl/dlibra/publication/129043/edition/143773>
- Volume II: <https://archive.org/details/operaquaesupersu02spin>
- Volume III: <https://commons.wikimedia.org/wiki/File:Benedicti_de_Spinoza_-_Opera_quae_supersunt_omnia_-_Carolus_Hermannus_Bruder_Vol_III_Tractatus_theologico-politicus._Compendium_grammatices_linguae_hebraeae,_1846.pdf>

The PDFs are not ingestion sources. They are kept only for provenance and page-level comparison. No new OCR or vision transcription is currently authorized; any future OCR would require the repository validation gate and could never enter the core corpus.
