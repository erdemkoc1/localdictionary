# Data and Model Licenses

The application code is MIT-licensed. Dictionary data and neural models are separate works and retain their own terms.

## Included sources

- Wiktionary/Kaikki extracts: CC BY-SA and GFDL terms, as applicable
- FreeDict EN/TR data: GPL-2.0-or-later
- Academic Word List mirror: CC0-1.0
- CEFR-J/Octanove data: source-specific attribution and CC BY-SA terms
- Opus-MT-derived models: CC BY 4.0

## Neural translation models

### OPUS-MT tc-big, Turkish to English (`translate-tr_en-tc-big`)

- Upstream model: `Helsinki-NLP/opus-mt-tc-big-tr-en`, trained by the Language Technology Research Group at the University of Helsinki.
- License: CC BY 4.0 (`LICENSES/CC-BY-4.0.txt`).
- Modification: converted to CTranslate2 format and quantised to int8. Weights were not retrained.
- Tokenizer files (`source.spm`, `target.spm`) are copied unchanged from the upstream repository.
- Attribution: Jörg Tiedemann and Yves Scherrer, "Building open translation services for the World: OPUS-MT" (EAMT 2020), and Jörg Tiedemann, "The Tatoeba Translation Challenge" (WMT 2020).

### Argos Translate, English to Turkish (`translate-en_tr-1_5`) and the older Turkish to English fallback (`translate-tr_en-1_5`)

- Packages from the Argos Translate project (<https://github.com/argosopentech/argos-translate>).
- The Argos Translate library is MIT-licensed. Confirm the individual package terms in the package `metadata.json` and upstream project before each release.

Only redistributable sources are included. Keep this file, the attribution records, and the applicable license texts with every redistributed database or model artifact.

See `LICENSES/` for the bundled license texts and `RELEASE_MANIFEST.json` for asset hashes.
