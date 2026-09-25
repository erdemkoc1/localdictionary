# Changelog

## 1.42.0-beta.1

- First launch now defaults to English; language selection persists locally.
- Global quick translation, context menu, and startup integrations are opt-in.
- Mutable user data moved to `%LOCALAPPDATA%\LocalDictionary` with safe migration.
- Removed the runtime Argos package-index path; local CTranslate2 inference is used directly.
- Removed restricted TDK/Webster database content from the public dataset.
- Added deterministic public-database cleanup, input limits, cache bounds, and concurrency guards.
- Added offline runtime tests, security audit, CodeQL/Dependabot workflows, and release checksums.
