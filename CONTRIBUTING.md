# Contributing

## Commit Message Convention

This repository mostly follows a Conventional Commits style:

```
<type>(<scope>): <subject>
```

Scope is optional:

```
<type>: <subject>
```

For `docs` and `build` commits, prefer no scope unless a scope is truly needed for clarity.

### 1. Types used in this repo

Use one of the commonly used types already present in history:

- `data`: data/content updates (most automation commits)
- `feat`: new features or behavior additions
- `fix`: bug fixes
- `docs`: documentation-only changes
- `build`: dependency/build-system updates

### 2. Scope style

Use lowercase, focused scopes that match the touched area.
Examples from this repo:

- game scope: `maimai`, `chunithm`, `ongeki`
- subsystem scope: `script`, `site`, `deps`
- nested scope when helpful: `script/maimai`, `site/chunithm`

When a change is in scripts and only affects one game, prefer nested scope:

- use `script/<game>` (for example `script/maimai`, `script/chunithm`, `script/ongeki`)
- avoid broad `script` or plain game scope if the script path is the primary area

### 3. Subject line style

- Keep it short and specific.
- Use lowercase sentence style (avoid title case).
- Do not end with a period.
- Describe the effective change, not implementation detail.

Examples:

- `fix(script/chunithm): wiki script breaking - handle exception where 解禁方法 is not listed in overview table`
- `fix(script/maimai): avoid false availability/date update logs`
- `feat(site): upgrade International ver. to CiRCLE`
- `data(maimai): add constants`
- `docs: clarify script scope rules`
- `build: bump dev dependencies`

### 4. Automation commit pattern

Automated data updates consistently use:

```
data(<game>): [bot] <action> <YYYYMMDD>
```

Examples:

- `data(maimai): [bot] add song extra data 20260319`
- `data(chunithm): [bot] update song constants`

If your change is manual (not workflow bot output), do not add `[bot]`.

### 5. Practical guidance

- Prefer one logical change per commit.
- If a commit mixes code + docs, choose the type by primary impact.
- Keep commit subjects compatible with existing history rather than introducing a new naming scheme.
