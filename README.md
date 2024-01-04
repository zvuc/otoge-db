<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/zvuc/ongeki-db/blob/master/img/ongeki-db-logo-2022-wob.svg?raw=true">
  <img alt="Ongeki DB Logo" src="https://github.com/zvuc/ongeki-db/blob/master/img/ongeki-db-logo-2022-bow.svg?raw=true" width="400">
</picture>

# Ongeki DB (https://ongeki.info)
This is a tool for viewing song information in SEGA's arcade music game 'Ongeki'. Based on the public data provided from the official homepage (https://ongeki.sega.jp/music/), this tool enables user to view information easier by using custom sort and filter options.

このツールは、SEGAの音ゲー「オンゲキ」の収録曲データをより便利に閲覧できるように制作されたビュアーです。

## How to fetch and apply new data
- You'll need Python 3.x to run scripts on command line.
- Install requirements
    ```
    pip install -r requirements.txt
    ```
- Run script to download JSON and new song images from server, then fetch additional data from wiki
    ```
    python scripts/update-songs.py --ongeki
    ```
    _Note: You may need to use `python3` instead of `python` depending on your environment (i.e.: macOS)_
    | Argument | Description |
    | --- | --- |
    | `--ongeki` `--chunithm` | Run script for specified game (Set only one at a time) |
    | `--nocolors` | _(Optional)_ Don't print colors to terminal messages |
    | `--escape` | _(Optional)_ Escape special characters for output (Song titles with symbols, etc) |
    | `--skipwiki` | _(Optional)_ Skip the wiki fetching part |

- Run script to fetch wiki data only (Enemy lv, Chart details, BPM)
    ```
    python scripts/update-wiki-data.py --ongeki
    ```
    | Argument | Description |
    | --- | --- |
    | `--ongeki` `--chunithm` | Run script for specified game (Set only one at a time) |
    | `--date_from` | _(Optional)_ Set start of date range to target songs. (Example: `--date_from 20230101`) If unset, script fetches for the latest datestamp in music-ex.json file. |
    | `--date_until` | _(Optional)_ Set end of date range to target songs. (Example: `--date_until 20231231`) If unset, script fetches for the latest datestamp in music-ex.json file. |
    | `--id` | _(Optional)_ Run script for a single song. Can't be used with the date range arguments above. (Example: `--id 2524`) |
    | `--nocolors` | _(Optional)_ Don't print colors to terminal messages |
    | `--escape` | _(Optional)_ Escape special characters for output (Song titles with symbols, etc) |

## Notes for Local Development
#### Build Scripts
- `yarn build` : minify+concat JS files, builds LESS stylesheet, runs PostCSS and minify.
- `yarn watch` : watches changes to stylesheet for local development

#### Local Dev Environment
Just open `index.html` and refresh manually. Simple as the good old year 2000.
Or, you can also do `python3 -m http.server` to quickly run a local server.

## Notes
- This webpage is hosted and run entirely on Github Pages without any additional backend servers attached.
- `{game_name}/data/music.json` : Copy of original JSON file provided by SEGA as-is
- `{game_name}/data/music-ex.json`: Augmented JSON file containing additional data (Enemy type / Enemy Lv. / Chart constants / BPM etc.)

## Credits
### Code Contributions
- [@Ryudnar](https://github.com/Ryudnar) : Early script foundation for song data downloading
- [@kiding](https://github.com/kiding/) : Script for updating datestamps after fetch
- [@ssankim](https://github.com/ssankim/) : Wiki fetch script & Github Actions workflow help

### Other Contributions & Data Sources
#### Ongeki
- [SEGA Official Ongeki website music data](https://ongeki.sega.jp/assets/data/music.json) : base JSON file
- [オンゲキ攻略wiki](https://wikiwiki.jp/gameongeki/) : BPM, Enemy type, Enemy Lv, Chart note details, Chart designer
- [オンゲキ譜面保管所](https://sdvx.in/ongeki.html) : Additional BPM, Chart designer info, Chart guide links
- [オンゲキbright MEMORY譜面定数表](https://docs.google.com/spreadsheets/d/1iG6CYz-pHSfLKz0m2bXipsoC_YicJWSMxNt2QJVI2ZE/) : Chart constants (譜面定数)
- Chart constants (譜面定数) reporters : [@RKS49019722](https://twitter.com/RKS49019722) [@Rinsaku471](https://twitter.com/Rinsaku471) [@46189_ext](https://twitter.com/46189_ext) [@hikkey7th](https://twitter.com/hikkey7th) [@suoineau_ac](https://twitter.com/suoineau_ac) [@hayato_ongeki](https://twitter.com/hayato_ongeki)

#### Chunithm
- [SEGA Official Music Data](https://ongeki.sega.jp/assets/data/music.json) : base JSON file
- [CHUNITHM攻略wiki](https://wikiwiki.jp/chunithmwiki/) : BPM, Chart note details, Chart constants, Chart designer
- [CHUNITHM譜面保管所](https://sdvx.in/chunithm.html) : Additional BPM, Chart designer info, Chart guide links
- [CHUNITHM LUMINOUS譜面定数表](https://docs.google.com/spreadsheets/d/1Nhr-lC1u11WPkUPVTatnNrKWCmVLglaA6hZHgh56N6w/edit#gid=262760047) : Chart constants (譜面定数)

### Special Thanks to
- [@u7gisan](https://twitter.com/u7gisan), [@TSUBAKI_ONGEKI](https://twitter.com/TSUBAKI_ONGEKI)

## Feedback
Contact [@zvuc_](https://twitter.com/zvuc_) for any suggestions or inquiries.

## Copyright
- MIT License for all code in this repository.
- All vector image assets used in this website have been produced independently from scratch, however intellectual rights for the original designs remain to SEGA.
- ONGEKI, CHUNITHM and the respective logos are trademarks of SEGA.
- All song jacket images are owned by SEGA and/or their respective owners.
- OTOGE DB is a fan project. It is not afilliated with nor endorsed by SEGA in any way.
