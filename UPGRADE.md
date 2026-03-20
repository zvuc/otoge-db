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

## Suggested quick checks

```bash
rg -n "CURRENT_JP_VER|CURRENT_INTL_VER" scripts/{game}/game.py
rg -n "game_version_display|game_version_display_intl" {game}/src/pug/_{game}_meta.pug
rg -n "version_list|CiRCLE PLUS" {game}/src/js/{game}.table-config.js
rg -n "VERSION_DATES|<NEW_CHUNITHM_VERSION_NAME>" scripts/chunithm/wiki.py
```
