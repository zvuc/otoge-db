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
    python scripts/main.py
    ```
    | Argument | Description |
    | --- | --- | 
    | `--nocolors` | Don't print colors to terminal messages |
    | `--skipwiki` | Skip the wiki fetching part |

- Run script to fetch wiki data (Enemy lv, Chart details, BPM)
    ```
    python scripts/update-wiki-data.py
    ```
    | Argument | Description |
    | --- | --- | 
    | `--date_from` | Set start of date range to target songs (Default: latest date in music-ex.json file) |
    | `--date_until` | Set end of date range to target songs (Default: latest date in music-ex.json file) |
    | `--id` | Explicitly specify a single song to update |
    | `--nocolors` | Don't print colors to terminal messages |

## Notes for Local Development
#### Build Scripts
- `build` : minify+concat JS files, builds LESS stylesheet, runs PostCSS and minify.
- `watch` : watches changes to stylesheet for local development

#### Local Dev Environment
Just open `index.html` and refresh manually. Simple as the good old year 2000.
Or, you can also do `python3 -m http.server` to quickly run a local server.

## Notes
- This webpage is hosted and run entirely on Github Pages without any additional backend servers attached.
- `/data/music.json` : Copy of original JSON file provided by SEGA
- `/data/music-ex.json`: Augmented JSON file containing additional data (Enemy type / lv / precise lv) (actually used file in the webpage)

## Credits
### Code Contributions
- [@Ryudnar](https://github.com/Ryudnar) : Base script for song data downloading
- [@kiding](https://github.com/kiding/) : Update datestamp on update
- [@ssankim](https://github.com/ssankim/) : Wiki fetch script & Github Actions workflow help

### Other Contributions & Data Sources
- [SEGA Official Music Data](https://ongeki.sega.jp/assets/data/music.json) : base JSON file
- [オンゲキ攻略wiki](https://wikiwiki.jp/gameongeki/) : Enemy type, level, chart detail info
- Precise chart level data (譜面定数) [@RKS49019722](https://twitter.com/RKS49019722) [@Rinsaku471](https://twitter.com/Rinsaku471) [@46189_ext](https://twitter.com/46189_ext) [@hikkey7th](https://twitter.com/hikkey7th) [@suoineau_ac](https://twitter.com/suoineau_ac) [@hayato_ongeki](https://twitter.com/hayato_ongeki)

### Special Thanks to
- [@u7gisan](https://twitter.com/u7gisan), [@TSUBAKI_ONGEKI](https://twitter.com/TSUBAKI_ONGEKI)

## Feedback
Contact [@zvuc_](https://twitter.com/zvuc_) for any suggestions or inquiries.

## Copyright
- MIT License for all code in this repository.
- All vector image assets used in this website are produced independently from scratch, however intellectual rights for the original designs are credited to SEGA.
- ONGEKI and ONGEKI Logo are trademarks of SEGA. All jacket images are owned by SEGA and/or their respective owners.
- ONGEKI DB is a fan project. It is not afilliated with nor endorsed by SEGA.
