# Third-Party Notices

LocalDictionary's own source code is distributed under the MIT License in
`LICENSE`. The Windows build also contains third-party runtime components.
Their notices remain applicable; the MIT license does not replace them.

| Component | Use | License / notice |
|---|---|---|
| CustomTkinter | GUI widgets | MIT (see `LICENSES/MIT-CustomTkinter.txt`) |
| darkdetect | System theme detection | BSD-3-Clause (see `LICENSES/BSD-3-Clause-darkdetect.txt`) |
| Pillow | Image support for the tray icon | HPND |
| pystray | Windows system tray integration | LGPL-3.0 (GPL-3.0 terms incorporated) |
| CTranslate2 | Local neural inference | MIT |
| SentencePiece | Local subword tokenization | Apache-2.0 (see `LICENSES/Apache-2.0.txt`) |

The release build excludes the Argos Translate package manager and its remote
package-index client. Translation models are data/model assets, not part of
the MIT-licensed source code; see `DATA_LICENSES.md` and the notices shipped
with the model directories. Full license texts referenced by the data and
component notices are collected in `LICENSES/`.
