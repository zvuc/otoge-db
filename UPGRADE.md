# Game Version Upgrade Playbook

Use this checklist whenever a game (maimai / CHUNITHM / オンゲキ) is upgraded to a new version.

## 1) Update current version constants in `scripts/{game}/game.py`

- File: `scripts/{game}/game.py`
- Update one of:
  - `CURRENT_JP_VER` (JP upgrade)
  - `CURRENT_INTL_VER` (INTL upgrade)

Example (maimai JP):

```py
CURRENT_JP_VER = "CiRCLE PLUS"
```

## 2) Update display version in `_{game}_meta.pug`

- File: `{game}/src/pug/_{game}_meta.pug`
- Update one of:
  - `game_version_display` (JP display)
  - `game_version_display_intl` (INTL display)

Example (maimai JP):

```pug
- var game_version_display = 'CiRCLE PLUS'
```

## 3) Update version mapping in `{game}.table-config.js` (if present)

- Find `const version_list` in `{game}/src/js/{game}.table-config.js`.
- If the new version is not listed, append it at the bottom.
- Follow the existing numeric pattern for the next key (commonly `+500` from previous entry).

Example (maimai):

```js
"26000": "CiRCLE",
"26500": "CiRCLE PLUS"
```

Note:
- In this repo, `const version_list` currently exists in `maimai/src/js/maimai.table-config.js`.
- If a game does not have `version_list`, skip this step for that game.

## 4) CHUNITHM only: append new version to `VERSION_DATES`

- File: `scripts/chunithm/wiki.py`
- Find the `VERSION_DATES` dict.
- Append the new version key/value at the bottom.
- Date format must be `YYYYMMDD` (version launch date).

Example:

```py
"X-VERSE-X": "20251211",
"NEXT-VERSION": "2026MMDD"
```

## 5) Clear constants for the upgraded game/region

Run:

```bash
yarn clear-const --{game} --{region}
```

Where:
- `{game}` is one of `--maimai`, `--chunithm`, `--ongeki`
- `{region}` is one of `--jp`, `--intl`

Examples:

```bash
yarn clear-const --maimai --jp
yarn clear-const --chunithm --intl
```

Note:
- `ongeki` has no INTL release currently. `--ongeki --intl` will fail by design.

## 6) Update version mapping in `scripts/{game}/chartguide.py` (CHUNITHM only)

- File: `scripts/chunithm/chartguide.py`
- Find `VERSION_MAPPING` dict.
- Append the new version key mapping to the internal numeric prefix code (commonly incremented by 1 for major versions, or kept the same for minor version upgrades).

Example:
```py
"VERSE": "10",
"X-VERSE": "10",
"X-VERSE-X": "10",
"MATE": "11"
```

## 7) Refresh Theme Colors in `{game}.less`

- File: `{game}/src/pug/_{game}_meta.pug` / `{game}/src/less/{game}.less`
- Pick theme colors from the official website of the new game version.
- Assign these to theme color variables (`--color-accent-*`) in `{game}/src/less/{game}.less` to match the brand identity.
- Refactor light and dark mode rules (e.g. form backgrounds, borders, active states, and buttons) to match the new color scheme, keeping them premium and legible in both theme modes.

## 8) Differentiate International Version Regional Style (If applicable)

- If the International version sits at the previous version while the JP version upgrades:
  - Uncomment the `:root[data-game-region="intl"]` styles override block in the Less stylesheet.
  - Define the legacy variable groups (e.g. `.variables-legacy-common()`, `.variables-legacy-light()`, `.variables-legacy-dark()`) using the previous version's color scheme.
  - This ensures users see the previous theme on the INTL region page and the new theme on the JP region page.

## 9) Separate Code and Data Commits

- Staging and committing changes should always split code changes from generated JSON database files:
  1. Stage and commit code/style changes first (commit prefix: `feat({game}): ...` or `fix({game}): ...`).
  2. Stage and commit JSON data changes separately (commit prefix: `data({game}): ...`).

## Suggested quick checks

```bash
rg -n "CURRENT_JP_VER|CURRENT_INTL_VER" scripts/{game}/game.py
rg -n "game_version_display|game_version_display_intl" {game}/src/pug/_{game}_meta.pug
rg -n "version_list|CiRCLE PLUS" {game}/src/js/{game}.table-config.js
rg -n "VERSION_DATES|<NEW_CHUNITHM_VERSION_NAME>" scripts/chunithm/wiki.py
rg -n "VERSION_MAPPING" scripts/chunithm/chartguide.py
```
