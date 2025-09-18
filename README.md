<p>
	<picture>
	  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/zvuc/otoge-db/blob/master/ongeki/img/ongeki-db-logo-2022-wob.svg?raw=true">
	  <img alt="Ongeki DB Logo" src="https://github.com/zvuc/otoge-db/blob/master/ongeki/img/ongeki-db-logo-2022-bow.svg?raw=true" width="200">
	</picture>
	&nbsp; &nbsp;<img alt="Chunithm DB Logo" src="https://github.com/zvuc/otoge-db/blob/master/chunithm/img/chunithm-db-logo.svg" style="margin-bottom:10px" width="240">
	&nbsp; &nbsp;<img alt="maimai DB Logo" src="https://github.com/zvuc/otoge-db/blob/master/maimai/img/maimai-db-logo.svg?raw=true" width="200">
</p>

# OTOGE DB (音ゲーDB)
OTOGE DB is an unofficial database for viewing song information served in SEGA's arcade music games 'Ongeki', 'Chunithm', 'maimai DX'. Building on top of the public data provided from the official SEGA websites and extra information available on various different community contributed sites, OTOGE DB allows convenient lookup of latest song information through the thoughtfully designed web interface.

OTOGE DBはSEGAの音ゲー「オンゲキ」「CHUNITHM」「maimaiでらっくす」の非公式収録曲データベースサイトです。公式サイトで公開されているデータを基にして、Wikiなどウェブで入手できる情報を集めて一箇所で楽に見れるようにする目標で作られました。

## Setting up dev environment
- You'll need Python 3.x to run scripts on command line.
- Install requirements
	```
	pip install -r requirements.txt
	```
	or
	```
	pip3 install -r requirements.txt
	```
- Setup virtual environment (if required)
	```
	python3 -m venv .venv
	```
- Activate venv
	```
	source .venv/bin/activate
	```

## Run scripts
- **`yarn fetch-songs`** : Download new song and images from server

	Arguments for all scripts:

	<table>
		<tr>
			<th width="200">Argument</th>
			<th>Description</th>
		</tr>
		<tr>
			<td><code>--ongeki</code><br><code>--chunithm</code><br><code>--maimai</code></td>
			<td><b>(Required)</b> Run script for specified game (Set only one at a time)</td>
		</tr>
		<tr>
			<td><code>--nocolors</code></td>
			<td>Don't print colors to terminal messages</td>
		</tr>
		<tr>
			<td><code>--markdown</code></td>
			<td>Print messages in Github flavored markdown format (for PR messages)</td>
		</tr>
		<tr>
			<td><code>--escape</code></td>
			<td>Escape unsafe characters for git message output (Song titles with symbols, etc)</td>
		</tr>
		<tr>
			<td><code>--no_timestamp</code></td>
			<td>Don't print timestamps on message output</td>
		</tr>
		<tr>
			<td><code>--no_verbose</code></td>
			<td>Only print significant changes and errors</td>
		</tr>
	</table>



- **`yarn fetch-intl`** : Fetch international version song availability & date info from [SilentBlue](https://silentblue.remywiki.com) (remywiki)

	Script specific-arguments:

	<table>
		<tr>
			<th width="200">Argument</th>
			<th>Description</th>
		</tr>
		<tr>
			<td><code>--strict</code></td>
			<td>Strict match songs by checking levels for all charts (If not set, script will proceed to update songs by just matching song title and artist names.)</td>
		</tr>
	</table>

- **`yarn fetch-wiki`** : Fetch extra song data from wiki

	Script specific-arguments:

	<table>
		<tr>
			<th width="200">Argument</th>
			<th>Description</th>
		</tr>
		<tr>
			<td><code>--date</code></td>
			<td>Set specific date to target songs. (Example: <code>--date 20230101</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--date_from</code></td>
			<td>Set start of date range to target songs. (Example: <code>--date_from 20230101</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--date_until</code></td>
			<td>Set end of date range to target songs. (Example: <code>--date_until 20231231</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--id</code></td>
			<td>Run script for a single song. Can't be used together with the date target arguments above. (Example: <code>--id 2524</code>)</td>
		</tr>
		<tr>
			<td><code>--all</code></td>
			<td>Run script for all songs. (Warning: may cause heavy traffic load to the wiki sites so may get you banned temporarily. Be careful especially when using with <code>--noskip</code>option!!)</td>
		</tr>
		<tr>
			<td><code>--noskip</code></td>
			<td>Don't skip items that already have URL</td>
		</tr>
		<tr>
			<td><code>--overwrite</code></td>
			<td>Overwrite keys that already have values</td>
		</tr>
	</table>

- **`yarn fetch-const`** : Fetch song constants

	Script specific-arguments:

	<table>
		<tr>
			<th width="200">Argument</th>
			<th>Description</th>
		</tr>
		<tr>
			<td><code>--date</code></td>
			<td>Set specific date to target songs. (Example: <code>--date 20230101</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--date_from</code></td>
			<td>Set start of date range to target songs. (Example: <code>--date_from 20230101</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--date_until</code></td>
			<td>Set end of date range to target songs. (Example: <code>--date_until 20231231</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--id</code></td>
			<td>Run script for a single song. Can't be used together with the date target arguments above. (Example: <code>--id 2524</code>)</td>
		</tr>
		<tr>
			<td><code>--overwrite</code></td>
			<td>Overwrite keys that already have values</td>
		</tr>
		<tr>
			<td><code>--clear_cache</code></td>
			<td>Clears local cache on run</td>
		</tr>
		<tr>
			<td><code>--legacy</code></td>
			<td>Match with legacy sgimera format</td>
		</tr>
	</table>

- **`yarn fetch-chartguide`** : Fetch chart guide links from [sdvx.in](https://sdvx.in/)

	Script specific-arguments:

	<table>
		<tr>
			<th width="200">Argument</th>
			<th>Description</th>
		</tr>
		<tr>
			<td><code>--date</code></td>
			<td>Set specific date to target songs. (Example: <code>--date 20230101</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--date_from</code></td>
			<td>Set start of date range to target songs. (Example: <code>--date_from 20230101</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--date_until</code></td>
			<td>Set end of date range to target songs. (Example: <code>--date_until 20231231</code>)<br>If unset, script fetches for the latest datestamp in music-ex.json file.</td>
		</tr>
		<tr>
			<td><code>--id</code></td>
			<td>Run script for a single song. Can't be used together with the date target arguments above. (Example: <code>--id 2524</code>)</td>
		</tr>
		<tr>
			<td><code>--overwrite</code></td>
			<td>Overwrite keys that already have values</td>
		</tr>
		<tr>
			<td><code>--clear_cache</code></td>
			<td>Clears local cache on run</td>
		</tr>
	</table>


## Notes for Local Development
#### Build Scripts
- `yarn build` : minify+concat JS files, builds LESS stylesheet, runs PostCSS and minify.
- `yarn watch` : watches changes to stylesheet for local development

#### Local Dev Environment
Just open `index.html` and refresh manually. Simple as the good old year 2000.
Or, you can also do `python -m http.server` to quickly run a local server.
_Note: You may need to use `python3` instead of `python` depending on your environment (i.e.: macOS)_

## Notes
- This webpage is hosted and run entirely on Github Pages without any additional backend servers attached.
- `{game_name}/data/music.json` and `maimai/data/maimai_songs.json` : Copy of original JSON file provided by SEGA as-is
- `{game_name}/data/music-ex.json`: Augmented JSON file containing additional data not provided by the official website
- `{game_name}/data/music-ex-intl.json`: Augmented JSON file containing song information for International version
- `{game_name}/data/music-ex-deleted.json`: JSON file containing deleted song information for archive purposes

## Credits
### Main Contributors
- [@mantou1233](https://github.com/Mantou1233/) : Bug reporting, data contributions, PR reviews, feature development
- [@ssankim](https://github.com/ssankim/) : Wiki fetch script & Github Actions workflow help
- [@kiding](https://github.com/kiding/) : Script for updating datestamps after fetch
- [@Ryudnar](https://github.com/Ryudnar) : Early script foundation for song data downloading

### Other Contributors
- [@u7gisan](https://twitter.com/u7gisan), [@TSUBAKI_ONGEKI](https://twitter.com/TSUBAKI_ONGEKI), [@RKS49019722](https://twitter.com/RKS49019722), [@Rinsaku471](https://twitter.com/Rinsaku471), [@46189_ext](https://twitter.com/46189_ext), [@hikkey7th](https://twitter.com/hikkey7th), [@suoineau_ac](https://twitter.com/suoineau_ac), [@hayato_ongeki](https://twitter.com/hayato_ongeki)

### Data Sources
#### Ongeki
- [SEGA Official Music Data](https://ongeki.sega.jp/assets/data/music.json) : base JSON file
- [オンゲキ攻略wiki](https://wikiwiki.jp/gameongeki/) : BPM, Enemy type, Enemy Lv, Chart note details, Chart designer
- [オンゲキ譜面保管所](https://sdvx.in/ongeki.html) : BPM, Chart designer, Chart guide links
- [オンゲキbright MEMORY Act.3 譜面定数表](https://docs.google.com/spreadsheets/d/1a7nDEG8N3QQUHl3WDwZedInX3_0EMSpU7qUuW89Lq3c) : Chart constants (譜面定数)

#### Chunithm
- [SEGA Official Music Data](https://ongeki.sega.jp/assets/data/music.json) : base JSON file
- [CHUNITHM攻略wiki](https://wikiwiki.jp/chunithmwiki/) : BPM, Chart note details, Chart designer
- [CHUNITHM譜面保管所](https://sdvx.in/chunithm.html) : BPM, Chart designer, Chart guide links
- [CHUNITHM LUMINOUS 譜面定数表](https://docs.google.com/spreadsheets/d/1Nhr-lC1u11WPkUPVTatnNrKWCmVLglaA6hZHgh56N6w) : Chart constants (譜面定数)
- [CHUNITHM VERSE 譜面定数表](https://docs.google.com/spreadsheets/d/1NTGkrOoLdzOoaYyz7d4vDT3cW2Q6lZfoc1nvd7nlNLE) : Chart constants (譜面定数)

#### maimai
- [SEGA Official Music Data](https://maimai.sega.jp/data/maimai_songs.json) : base JSON file
- [maimai 攻略wiki](https://gamerch.com/maimai/) : BPM, Chart note details, Chart designer
- [maimai DX PRiSM譜面定数表](https://docs.google.com/spreadsheets/d/1DKssDl2MM-jjK_GmHPEIVcOMcpVzaeiXA9P5hmhDqAo) : Chart constants (譜面定数)
- [内部Lv.の表 PRiSM ver.(sgimera)](https://sgimera.github.io/mai_RatingAnalyzer/maidx_inner_level_23_prism.html) : Chart constants (譜面定数)

## Feedback
- Contact [@otoge_db](https://x.com/otoge_db) or [@zvuc_](https://x.com/zvuc_) for any suggestions or inquiries.
- お問い合わせなどは上記のアカウントまでお願いします。

## Copyright
- MIT License for all code in this repository.
- All vector image assets used in this website have been produced independently from scratch, however intellectual rights for the original designs remain to SEGA.
- ONGEKI, CHUNITHM, maimai でらっくす and the respective logos are trademarks of SEGA.
- All song jacket images are owned by SEGA and/or their respective owners.
- OTOGE DB is a fan project. It is not afilliated with nor endorsed by SEGA in any way.
- OTOGE DBは非公式ファンメイドプロジェクトです。株式会社セガもしくは他の関連会社との関係はありません。
