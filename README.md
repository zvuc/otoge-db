# Ongeki Song DB Table
This is a tool for viewing song information in SEGA's arcade music game 'Ongeki'. Based on the public data provided from the official homepage (https://ongeki.sega.jp/music/), this tool enables user to view information easier by using custom sort and filter options.

このツールは、SEGAの音ゲー「オンゲキ」の収録曲データをより便利に閲覧できるように制作されたビュアーです。

## Data Sources
- Base data source: https://ongeki.sega.jp/assets/data/music.json
- Enemy type & level data: [オンゲキ攻略wiki](https://ongeki.gamerch.com/%E5%B1%9E%E6%80%A7%E5%88%A5%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7)
- Detailed chart integers (譜面定数): [OngekiScoreLog](https://ongeki-score.net/music)
- Combined Data Sheet → [https://docs.google.com/spreadsheets/d/1ZyASbNVyZVuFJ_bwka48sW4_jCBhSSsadLCQTXLA9FY]

## Script command to batch download album art images
```
curl -O https://ongeki.sega.jp/assets/img/music/\[0001-0047\].jpg
curl -O https://ongeki.sega.jp/assets/img/music/\[0048-0107\].png
curl -O https://ongeki.sega.jp/assets/img/music/\[0108-0175\].jpg
```

## Notes
- `/data/music.json` : Original JSON file provided by SEGA
- `/data/music-ex.csv`: Combined data sheet exported to CSV (includes extra info)
- `/data/music-ex.json`: Above CSV back-converted to JSON (actually used file in the webpage)

## Contribution & Feedback
Contact [@zvuc_](https://twitter.com/zvuc_) for inquiries.
提案や合同作業など興味ある方はツイッターで連絡ください。

