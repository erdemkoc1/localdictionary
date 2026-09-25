# Third-Party Notices

LocalDictionary's own source code is distributed under the MIT License in
`LICENSE`. The Windows build also contains third-party runtime components.
Their notices remain applicable; the MIT license does not replace them.

| Component | Use | License / notice |
|---|---|---|
| CustomTkinter | GUI widgets | CC0-1.0 (package metadata) |
| darkdetect | System theme detection | MIT |
| Pillow | Image support for the tray icon | HPND |
| pystray | Windows system tray integration | LGPL-3.0 |
| CTranslate2 | Local neural inference | MIT |
| SentencePiece | Local subword tokenization | Apache-2.0 |

The release build excludes the Argos Translate package manager and its remote
package-index client. Translation models are data/model assets, not part of
the MIT-licensed source code; see `DATA_LICENSES.md` and the notices shipped
with the model directories.
