# Ongeki Song DB Table
This is a tool for viewing song information in SEGA's arcade music game 'Ongeki'. Based on the public data provided from the official homepage (https://ongeki.sega.jp/music/), this tool enables user to view information easier by using custom sort and filter options.

このツールは、SEGAの音ゲー「オンゲキ」の収録曲データをより便利に閲覧できるように制作されたビュアーです。

## Data Sources
- Base data source: https://ongeki.sega.jp/assets/data/music.json
- Enemy type & level data: [オンゲキ攻略wiki](https://ongeki.gamerch.com/%E5%B1%9E%E6%80%A7%E5%88%A5%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7)
- Precise LV data (譜面定数): [OngekiScoreLog](https://ongeki-score.net/music), Twitter for latest data (Mostly [@masa_9713](https://twitter.com/masa_9713))

## How to fetch and apply new data
- You'll need Python3 to run scripts on command line.
- Install requirements
    ```
    pip3 install requests
    ```
- Run script to download JSON and new song images from server
    ```
    python3 scripts/main.py
    ```

## Notes for Local Development
#### Build Scripts
`build` : builds LESS stylesheet and runs PostCSS.
`watch` : watches changes to stylesheet for local development

#### Local Dev Environment
Just open `index.html` and refresh manually. Simple as the good old year 2000.

## Notes
- This webpage is hosted and run entirely on Github Pages without any additional backend servers attached.
- `/data/music.json` : Copy of original JSON file provided by SEGA
- `/data/music-ex.json`: Augmented JSON file containing additional data (Enemy type / lv / precise lv) (actually used file in the webpage)

## Contributors
- [@Ryudnar](https://github.com/Ryudnar) : song data download automation script
- [@kiding](https://github.com/kiding/) : auto update datestamp

## Feedback
Contact [@zvuc_](https://twitter.com/zvuc_) for inquiries.

## Copyright
MIT License for all code in this repository.
All image assets and other copyrighted materials are owned by SEGA or their respective owners.

