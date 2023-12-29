$(document).ready(function() {
    var searchParams = new URLSearchParams(window.location.search);

    var columns_params = [
        { 
            displayTitle: "ID (system)",
            name: "id",
            data: "id",
            className: "id detail-hidden",
            visible: false
        },
        { 
            displayTitle: "#",
            name: "index",
            data: "id",
            className: "id detail-hidden",
            data: function(row) {
                return row.id;
            },
            render: renderInWrapper(),
            width: "20px",
            searchable: false,
            visible: false
        },
        { 
            displayTitle: "アルバムアート",
            name: "jacket",
            data: "image_url",
            className: "jacket detail-hidden",
            render: function(data) {
                return '<span class="img-wrap"><img src=\"jacket/' + data + '\"\/><\/span>';
            },
            width: "50px",
            orderable: false,
            searchable: false
        },
        { 
            displayTitle: "曲名",
            name: "title",
            data: "title",
            className: "song-title detail-hidden",
            render: function ( data, type, row ) {
                // If display or filter data is requested, return title
                if ( type === 'display' ) {
                    return '<div class="inner-wrap">' +
                            ( row.bonus == "1" ? '<span class="bonus">BONUS<\/span>' : "") +
                            '<span class="title">' + data + '<\/span>' +
                            '<span class="dash hidden"> - <\/span>' +
                            '<span class="artist-display hidden">' + row.artist + '<\/span>'+
                        '<\/div>';
                }
                else if ( type === 'filter' ) {
                    return data;
                }
                // Else type detection or sorting data, return title_sort
                else {
                    return row.title_sort;
                }
            },
            width: "80vw"
        },
        {
            displayTitle: "曲名 (読み)",
            name: "title_sort",
            data: "title_sort",
            className: "title-sort",
            visible: false,
            searchable: false
        },
        { 
            // redundant (fake) merged title column for mobile
            displayTitle: "アーティスト",
            name: "title_merged",
            data: "title",
            className: "artist detail-hidden",
            render: function ( data, type, row ) {
                // If display or filter data is requested, return title
                if ( type === 'display' ) {
                    return '<div class="inner-wrap"><span class="artist-display hidden">' + row.artist + '<\/span><\/div>';
                }
                else {
                    return row.title_sort;
                }
            },
            searchable: false
        },
        { 
            displayTitle: "BPM",
            name: "bpm",
            data: "bpm",
            className: "details bpm",
            searchable: false,
            visible: false
        },
        { 
            displayTitle: "バージョン",
            name: "version",
            data: "version",
            className: "details version",
            filterable: true,
            render: renderInWrapper(),
            customDropdownSortSource: "date",
            width: "12em"
        },
        { 
            displayTitle: "ジャンル",
            name: "category",
            data: "category",
            className: "category",
            render: renderInWrapper(),
            customDropdownSortSource: 'category_id',
            filterable: true
        },
        { 
            displayTitle: "ジャンルID",
            name: "category_id",
            data: "category_id",
            width: "90px",
            visible: false
        },
        { 
            displayTitle: "チャプターID",
            name: "chap_id",
            data: "chap_id",
            className: "chapter-id",
            visible: false
        },
        {
            // combine chap_id + chapter
            displayTitle: "チャプター",
            name: "chap",
            data: function( row, type, set, meta ) {
                if ( type === 'sort' || type === 'meta') {
                    return row.chap_id;
                } else {
                    var chap_id_display = parseChapId(row, true);
                    return chap_id_display + row.chapter
                }
            },
            className: "chapter",
            width: "15em",
            render: function ( data, type, row ) {
                if ( type === 'display' ) {
                    var chap_id_display = parseChapId(row, true);
                    return '<div class="inner-wrap"><span class="chap-id-badge">' + chap_id_display + '<\/span><span class="chap-name">' + row.chapter + '<\/span><\/div>';
                }
                else {
                    return data;
                }
            },
            filterable: true
        },
        { 
            displayTitle: "属性",
            name: "enemy_type",
            data: "enemy_type",
            className: "chara type",
            render: function ( data, type, row ) {
                if ( type === 'display' ) {
                    return '<div class="inner-wrap"><span class="element-type-icon ' + data.toLowerCase() + '"><span class="icon"><\/span><span class="label-text">' + data + '<\/span><\/span></div>';
                }
                // use chara_id for sort
                else {
                    return data;
                }
            },
            width: "40px",
            filterable: true
        },
        { 
            displayTitle: "キャラID",
            name: "chara_id",
            data: "chara_id",
            visible: false
        },
        { 
            displayTitle: "相手キャラ",
            name: "character",
            data: "character",
            className: "chara character",
            render: function ( data, type, row ) {
                if ( type === 'display' ) {
                    return '<div class="inner-wrap">' + data + '<\/div>';
                }
                // use chara_id for sort
                else {
                    return data;
                }
            },
            customDropdownSortSource: 'chara_id',
            width: "10em",
            filterable: true
        },
        { 
            displayTitle: "相手レベル",
            name: "enemy_lv",
            data: "enemy_lv",
            className: "chara enemy-lv",
            render: function ( data, type, row ) {
                if ( type === 'display' ) {
                    return '<div class="inner-wrap">Lv.' + data + '<\/div>';
                }
                // use chara_id for sort
                else {
                    return data;
                }
            },
            customDropdownSortSource: sortByLeadingZeros('enemy_lv'),
            width: "4em"
        },
        { 
            //  BASIC
            displayTitle: "BASIC",
            name: "lev_bas",
            data: sortLevels('lev_bas', 'lev_bas_i'),
            className: "lv lv-bsc",
            render: renderLvNum('lev_bas', 'lev_bas_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_bas'),
            reverseSortOrder: true,
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  ADVANCED
            displayTitle: "ADVANCED",
            name: "lev_adv",
            data: sortLevels('lev_adv', 'lev_adv_i'),
            className: "lv lv-adv",
            render: renderLvNum('lev_adv', 'lev_adv_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_adv'),
            reverseSortOrder: true,
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  EXPERT
            displayTitle: "EXPERT",
            name: "lev_exc",
            data: sortLevels('lev_exc', 'lev_exc_i'),
            className: "lv lv-exp",
            render: renderLvNum('lev_exc', 'lev_exc_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_exc'),
            reverseSortOrder: true,
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  MASTER
            displayTitle: "MASTER",
            name: "lev_mas",
            data: sortLevels('lev_mas', 'lev_mas_i'),
            className: "lv lv-mas",
            render: renderLvNum('lev_mas', 'lev_mas_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_mas'),
            reverseSortOrder: true,
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  LUNATIC
            displayTitle: "LUNATIC",
            name: "lev_lnt",
            data: sortLevels('lev_lnt', 'lev_lnt_i'),
            className: "lv lv-lnt",
            render: renderLvNum('lev_lnt', 'lev_lnt_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_lnt'),
            reverseSortOrder: true,
            width: "3rem",
            filterable: flat_view ? false : true
        },
        {
            //  chart_diff
            displayTitle: "譜面",
            name: "chart_diff",
            data: 
                function( row, type, set, meta ) {
                    if ( flat_view == true ) {
                        if ( type === 'sort' || type === 'meta') {
                            return row.chart_diff;
                        } 
                        else {
                            return convertDifficultyNames(row.chart_diff);
                        }
                    } else {
                        return null;
                    }
                },
            className: "lv-name detail-hidden",
            width: "3rem",
            createdCell: flat_view ? ( function( td, cellData, rowData, row, col ) {
                $(td).addClass( rowData.chart_diff );
            }) : null,
            render: flat_view ? renderChartDifficultyName('chart_diff') : null,
            customDropdownSortSource: flat_view ? sortByDifficultyCategory('chart_diff') : null,
            searchable: flat_view,
            filterable: flat_view,
            visible: false
        },
        {
            //  chart_lev (for sort)
            displayTitle: "難易度グループ",
            name: "chart_lev",
            data: ( flat_view ? 'chart_lev' : null ),
            className: "lv detail-hidden",
            width: "4rem",
            customDropdownSortSource: sortByLeadingZeros('chart_lev'),
            reverseSortOrder: true,
            filterable: false,
            visible: false
        },
        {
            //  chart_lev_i
            displayTitle: "譜面レベル",
            name: "chart_lev_i",
            data: ( flat_view ? 'chart_lev_i' : null ),
            className: "lv lv-name detail-hidden",
            render: ( flat_view ? renderChartDifficultyNameAndLv('chart_diff', 'chart_lev', 'chart_lev_i', 'chart_lev_i_display')
            : null ),
            width: "4rem",
            createdCell: flat_view ? ( function( td, cellData, rowData, row, col ) {
                $(td).addClass( rowData.chart_diff );
            }) : null,
            filterable: false,
            searchable: false,
            visible: flat_view
        },
        { 
            displayTitle: "NEW",
            name: "new",
            data: "new",
            searchable: false,
            visible: false
        },
        { 
            displayTitle: "ノート数",
            name: "chart_notes",
            data: ( flat_view ? "chart_notes" : null ),
            className: "details notecount detail-hidden",
            width: "6em",
            searchable: false,
            visible: false
        },
        { 
            displayTitle: "ベル",
            name: "chart_bells",
            data: ( flat_view ? "chart_bells" : null ),
            className: "details notecount detail-hidden",
            width: "5em",
            searchable: false,
            visible: false
        },
        { 
            displayTitle: "譜面作者",
            name: "chart_designer",
            data: ( flat_view ? "chart_designer" : null ),
            width: "15em",
            className: "details detail-hidden",
            filterable: flat_view,
            searchable: flat_view,
            visible: false
        },
        { 
            displayTitle: "追加日",
            name: "date",
            // data: "date",
            data: function( row, type, set, meta ) {
                return formatDate(row.date)
            },
            className: "date",
            filterable: true,
            // render: DataTable.render.date('yyyyMMDD','yyyy-MM-DD'),
            render: function ( data, type, row ) {
                if ( type === 'display' ) {
                    return '<div class="inner-wrap">'+ data +'<\/div>';
                }
                else {
                    return data;
                }
            },
            reverseSortOrder: true,
            width: "4em"
        },
        { 
            displayTitle: "BONUS",
            name: "bonus",
            data: "bonus",
            className: "details detail-hidden",
            width: "10px"
        }
    ];

    var default_order = 
        flat_view ?
            [[23, 'desc'],[15, 'desc'],[28, 'desc']] :
            [[28, 'desc'],[10, 'asc'],[0, 'asc']];

    function checkPropertyAndValueExists(json, property) {
        if (json.hasOwnProperty(property)) {
            return json[property] !== "" ? true : false;
        } else {
            return false;
        }
    }
    
    function sortLevels(col_a, col_b) {
        return function ( row, type, set, meta ) {
            if ( type === 'sort' ) {
                if ( row[col_b] === "" ) {
                    return addLeadingZero(row[col_a]);
                } else {
                    return addLeadingZero(row[col_b]);
                }
            }
            else {
                return row[col_a];
            }
        }
    }

    function addLeadingZero(s) {
        if(s != "") {
            lev_processed = parseInt(s) < 10 ? ('0' + s) : s;
            return lev_processed;
        } else {
            return "";
        }
    }

    function sortByLeadingZeros(column) {
        return function (row_a, row_b) {
            return addLeadingZero(row_a[column]).localeCompare(addLeadingZero(row_b[column]));
        }
    }

    function renderLvNum(simple_lv, precise_lv) {
        return function ( data, type, row ) {
            if ( type === 'display' ) {
                return '<div class="inner-wrap"><span class="lv-num-simple">' + row[simple_lv] + '<\/span><span class="lv-num-precise">' + row[precise_lv] + '<\/span><\/div>';
            }
            else {
                return data;
            }
        }
    }

    function renderChartDifficultyNameAndLv(chart_diff, simple_lv, precise_lv, precise_lv_display) {
        return function ( data, type, row ) {
            if ( type === 'display' ) {
                var chart_diff_display = convertDifficultyNames(row[chart_diff]);                

                return '<div class="inner-wrap"><span class="diff-name">' + chart_diff_display + '</span><span class="lv-num-wrap"><span class="lv-num-simple">' + row[simple_lv] + '<\/span><span class="lv-num-precise">' + row[precise_lv_display] + '<\/span></span><\/div>';
            }
            else {
                return data;
            }
        }
    }

    function renderChartDifficultyName(chart_diff) {
        return function ( data, type, row ) {
            if ( type === 'display' ) {
                var chart_diff_display = convertDifficultyNames(row[chart_diff]);       

                return '<span class="diff-name">' + chart_diff_display + '</span>';
            }
            else {
                return data;
            }
        }
    }

    function convertDifficultyNames(src,sort) {
        if ( !sort ) {
            switch (src) {
                case 'lev_bas' :
                    var chart_diff_display = 'BASIC'
                    break;
                case 'lev_adv' :
                    var chart_diff_display = 'ADVANCED'
                    break;
                case 'lev_exc' :
                    var chart_diff_display = 'EXPERT'
                    break;
                case 'lev_mas' :
                    var chart_diff_display = 'MASTER'
                    break;
                case 'lev_lnt' :
                    var chart_diff_display = 'LUNATIC'
                    break;
            }
        } else {
            switch (src) {
                case 'lev_bas' :
                    var chart_diff_display = '1 BASIC'
                    break;
                case 'lev_adv' :
                    var chart_diff_display = '2 ADVANCED'
                    break;
                case 'lev_exc' :
                    var chart_diff_display = '3 EXPERT'
                    break;
                case 'lev_mas' :
                    var chart_diff_display = '4 MASTER'
                    break;
                case 'lev_lnt' :
                    var chart_diff_display = '5 LUNATIC'
                    break;
            }
        }

        return chart_diff_display;
    }

    function sortByDifficultyCategory(column) {
        return function (row_a, row_b) {
            return convertDifficultyNames(row_a[column],true).localeCompare(convertDifficultyNames(row_b[column],true));
        }
    }

    function renderInWrapper() {
        return function ( data, type, row ) {
            if ( type === 'display' ) {
                return '<div class="inner-wrap">' + data + '<\/div>';
            }
            else {
                return data;
            }
        }
    }

    function flattenMusicData(data, flat_view) {
        if (flat_view) {
            return data
                .map(obj =>
                    ['lev_bas', 'lev_adv', 'lev_exc', 'lev_mas', 'lev_lnt']
                        .map(chart_diff => processChartData(obj, chart_diff))
                )
                .flat()
                .filter(obj => !!obj);
        } else {
            return data;
        }
    }

    function processChartData(obj, chart_diff) {
        if (obj[chart_diff]) {
            return {
                ...obj,
                chart_diff,
                chart_lev: obj[chart_diff],
                chart_lev_i: parseFloat(obj[`${chart_diff}_i`] || obj[chart_diff].replace('+', '.7')),
                chart_lev_i_display: obj[`${chart_diff}_i`] || `<span class="approx">${parseFloat(obj[chart_diff].replace('+', '.7')).toFixed(1)}</span>`,
                chart_notes: obj[`${chart_diff}_notes`],
                chart_bells: obj[`${chart_diff}_bells`],
                chart_designer: obj[`${chart_diff}_designer`]
            };
        }
        return null;
    }

    function parseChapId(row, includeTrailingSpace) {
        var chap_id = row.chap_id;
        var chap_chapter = chap_id.substr(3,2);

        // 0xxxx : Normal chapters
        if (chap_id.substr(0,1) == "0") {
            var chap_book = chap_id.substr(1,1);

            // 0xx8x : side chapter
            if (chap_id.substr(3,1) == "8") {
                var chap_book = chap_id.substr(1,1);
                var chap_chapter = 'S' + chap_id.substr(4,1);
            }

            // 0xxxx: chapters
            if (chap_book > "0") {
                return chap_book + '-' + chap_chapter + (includeTrailingSpace ? ' ' : '');
            } 
            // 00xxx : default mylist
            else {
                return '';
            }
        }
        // 70xxx : Memory chapters
        else if (chap_id.substr(0,2) == "70") {
            var chap_book = "M";
            return chap_book + '-' + chap_chapter + (includeTrailingSpace ? ' ' : '');
        }
        // 80xxx : Event chapters
        else if (chap_id.substr(0,2) == "80") {
            var chap_book = "SP2";
            return chap_book + '-' + chap_chapter + (includeTrailingSpace ? ' ' : '');
        }
        // 99xxx : Event chapters
        else if (chap_id.substr(0,2) == "99") {
            var chap_book = "SP";
            return chap_book + '-' + chap_chapter + (includeTrailingSpace ? ' ' : '');
        }
        // Others?
        else {
            return chap_id + (includeTrailingSpace ? ' ' : '');
        }
    }

    function formatDate(inputDate, dateFormat) {
        // Parse input date string
        var year = inputDate.slice(0, 4);
        var month = inputDate.slice(4, 6);
        var day = inputDate.slice(6, 8);
        var ISOdate = `${year}-${month}-${day}`

        // Format the date as "YYYY-MM-DD"
        if (dateFormat == 'JP') {
            var days_of_week = ["日", "月", "火", "水", "木", "金", "土"];
            var current_year = new Date().getFullYear();
            var day_of_week = days_of_week[new Date(ISOdate).getDay()];
            var year_print = (current_year == year) ? '' : `${year}/`;
            var formatted_date = year_print + `${month}/${day}(${day_of_week})`;
        }
        else {
            var formatted_date = ISOdate;
        }

        return formatted_date;
    }

    $.getJSON("data/music-ex.json", (data) => {
        

        var table = $('#table').DataTable( {
            // "ajax": {
            //     url: "data/music-ex.json",
            //     dataSrc: ""
            // },
            data: flattenMusicData(data, flat_view),
            "buttons": [
                // {
                //     extend: 'colvisRestore',
                //     text: '全カラムON',
                // },
                // {
                //     extend: 'colvisGroup',
                //     text: '全レベル ON',
                //     show: [ 14, 15, 16, 17, 18 ]
                // },
                // {
                //     extend: 'colvisGroup',
                //     text: '譜面レベルのみ',
                //     hide: [ 6, 8, 9, 10, 12, 13, 24 ],
                //     show: [ 14, 15, 16, 17, 18 ],
                // },
                // {
                //     extend: 'colvisGroup',
                //     text: 'EXPERT以上のみ',
                //     hide: [ 6, 8, 9, 10, 12, 13, 14, 15, 24 ],
                //     show: [ 16, 17, 18 ]
                // },
                // {
                //     extend: 'colvisGroup',
                //     className: 'asdf',
                //     text: 'ジャンル・チャプタ OFF',
                //     hide: [ 6, 9 ]
                // },
                // {
                //     extend: 'colvisGroup',
                //     className: 'asdf',
                //     text: '属性・Lv ON',
                //     show: [ 10, 13 ]
                // },
                {
                    extend: 'colvis',
                    className: 'config-btn',
                    columns: '.toggle',
                    text: 'カラムON/OFF',
                    collectionTitle: "表示するカラムを選択",
                    collectionLayout: "fixed",
                    fade: 150
                },
            ],
            "columns": columns_params,
            "deferRender": true,
            "dom": '<"toolbar-group"<"toolbar filters"><"toolbar search"f>><"toolbar secondary"<"info"ilB>><"table-inner"rt><"paging"p>',
            "language": {
                "sEmptyTable":     "テーブルにデータがありません",
                "sInfo":           " _TOTAL_項目 (_START_〜_END_ 表示中)",
                "sInfoEmpty":      " 0 項目",
                "sInfoFiltered":   "（全 _MAX_ 項目）",
                "sInfoPostFix":    "",
                "sInfoThousands":  ",",
                "sLengthMenu":     "1ページ表示 _MENU_",
                "sLoadingRecords": "読み込み中...",
                "sProcessing":     "処理中...",
                "sSearch":         "キーワード検索",
                "sZeroRecords":    "一致するレコードがありません",
                "oPaginate": {
                    "sFirst":    "先頭",
                    "sLast":     "最終",
                    "sNext":     "次",
                    "sPrevious": "前"
                },
                "oAria": {
                    "sSortAscending":  ": 列を昇順に並べ替えるにはアクティブにする",
                    "sSortDescending": ": 列を降順に並べ替えるにはアクティブにする"
                }
            },
            "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
            "order": default_order, 
            "responsive": {
                details: {
                    type: 'column',
                    target: 'tr',
                    display: $.fn.dataTable.Responsive.display.modal( {
                        header: function ( row ) {
                            var data = row.data();
                            var encoded_title = encodeURIComponent(
                                data.title
                                .replaceAll('&', '＆')
                                .replaceAll(':', '：')
                                .replaceAll('[','［')
                                .replaceAll(']','］')
                                .replaceAll('#','＃')
                                .replaceAll('"','”')
                            );
                            var wiki_url_guess = 'https:\/\/wikiwiki.jp\/gameongeki\/' + encoded_title;

                            var wiki_url = data['wikiwiki_url'] ? data['wikiwiki_url'] : wiki_url_guess;


                            return '<div class="modal-header" style="--img:url(jacket/' + data.image_url + ');"><span class="header-img"></span><span class="header-img-overlay"></span><div class="img-wrap">' + 
                                '<img src=\"jacket/' + data.image_url + '\"\/>' +
                                '<\/div><div class="content-wrap">' +
                                ( data.bonus == "1" ? '<span class="bonus">BONUS<\/span>' : "") +
                                '<span class="title">' + data.title + '<\/span>' +
                                '<span class="artist">' + data.artist + '<\/span>' +
                                ( data.copyright1 !== "-" ? '<span class="copyright">' + data.copyright1.replace(/\s+ピアプロロゴ/, '<span class="piapro">piapro</span>') + '<\/span>' : '' ) +
                                '<div class="quicklinks">' +
                                '<a class="wiki" href="' + wiki_url + '" target="_blank" rel="noopener noreferer nofollow">Wiki<\/a>' +
                                '<a class="youtube" href="https:\/\/youtube.com\/results?search_query=オンゲキ+譜面確認+' + encoded_title + '" target="_blank" rel="noopener noreferer nofollow"><\/a>' +
                                '<\/div>' +
                                '<\/div><\/div>'
                        },
                        footer: function ( row ) {
                            var data = row.data();
                            return '<div class="modal-footer">' +
                                '<div class="report"><a class="report-btn" href="https:\/\/twitter.com\/intent\/tweet?text=@zvuc_%0A%E3%80%90%23%E3%82%AA%E3%83%B3%E3%82%B2%E3%82%ADDB%20%E6%83%85%E5%A0%B1%E6%8F%90%E4%BE%9B%E3%80%91%0A%E6%9B%B2%E5%90%8D%EF%BC%9A' + encodeURIComponent(data.title) +'%0A%E8%AD%9C%E9%9D%A2%EF%BC%9A" target="_blank" rel="noopener noreferer nofollow">💬 足りない情報・間違いを報告する （Twitter）<\/a><\/div>' +
                                '<\/div>'
                        }
                    } ),
                    // renderer: $.fn.dataTable.Responsive.renderer.tableAll()
                    renderer: function(api, rowIdx, columns) {
                        var row = api.row(rowIdx);
                        var data = row.data();
                        var chara_id = data['chara_id'];
                        var enemy_type = data['enemy_type'];
                        var lunatic = data['lev_lnt'] !== "" ? "lunatic" : "";

                        var normalRows = $.map(columns, function(col, i) {
                            var column_param = columns_params[col.columnIndex];

                            // generic
                            if (!col.className.includes('detail-hidden') && !col.className.includes('lv ') && !col.className.includes('chara ')) {
                                return '<div class="row ' + col.className + '" data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                                '<span class="row-label">' + col.title + '</span> ' + '<span>' + col.data + '</span>' +
                                '</div>'
                            }
                        }).join('');

                        var charaRows = $.map(columns, function(col, i) {
                            var column_param = columns_params[col.columnIndex];

                            // chara
                            if (!col.className.includes('detail-hidden') && col.className.includes('chara ')) {
                                return '<div class="row ' + col.className + '" data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                                '<span class="row-label">' + column_param.displayTitle + '</span> ' + '<span>' + col.data + '</span>' +
                                '</div>'
                            }
                        }).join('');

                        var chartRows = $.map(columns, function(col, i) {
                            var column_param = columns_params[col.columnIndex];

                            // lv display
                            if (!col.className.includes('detail-hidden') && col.className.includes('lv ')) {
                                var chart_name = column_param['name'];

                                var notes = chart_name.concat('_notes');
                                var bells = chart_name.concat('_bells');
                                var designer = chart_name.concat('_designer');
                                var chartLink = chart_name.concat('_chart_link');                                

                                return '<div class="row ' + col.className + '" data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                                    '<span class="row-label"><span>' + column_param.displayTitle + '</span></span> ' + 
                                    '<span class="content-col">' +
                                        '<span class="main-info-wrap">' + col.data + '</span>' +
                                        '<span class="sub-info-wrap">' +
                                            ( checkPropertyAndValueExists(data, notes) ? '<span class="notes"><span class="label">Chain</span><span>' + data[notes] + '</span></span>' : "") +
                                            ( checkPropertyAndValueExists(data, bells) ? '<span class="bells"><span class="label">Bell</span><span>' + data[bells] + '</span></span>' : "") +
                                            ( checkPropertyAndValueExists(data, designer) ? '<span class="designer"><span class="label">Designer</span><span>' + data[designer] + '</span></span>' : "") +
                                        '</span>' +
                                    '</span>' +
                                    ( checkPropertyAndValueExists(data, chartLink) ? '<span class="chart-link"><a class="btn chartlink" target="_blank" rel="noopener noreferrer" href="https://sdvx.in/ongeki/'+ data[chartLink] +'.htm"><span class="img"></span><span>譜面確認</span></a><span class="chart-provider">sdvx.in 提供</span></span>' : "") +
                                    '</div>'
                            }
                        }).join('');

                        var combinedRows = $('<div class="table-wrapper"/>')
                                                .append(
                                                    $('<div class="details-table chara-details"/>')
                                                        .append('<div class="table-header"><span class="th-label">CHARACTER</span></div>')
                                                        .append(charaRows)
                                                        .append(chara_id.substr(0,1) == "1" ? '<span class="chara-img '+ enemy_type.toLowerCase() +'" style="--chara-img: url(\'./img/chara/' + chara_id + '.png\');"></span>': "")
                                                )
                                                .append(
                                                    $('<div class="details-table chart-details '+ lunatic +'"/>')
                                                        .append('<div class="table-header"><span class="th-label">CHART</span></div>')
                                                        .append(chartRows)
                                                )
                                                .append(
                                                    $('<div class="details-table misc-details"/>')
                                                        .append('<div class="table-header"><span class="th-label">SONG METADATA</span></div>')
                                                        .append(normalRows)
                                                );

                        return combinedRows ?
                            combinedRows :
                            false;
                    }
                }
            },
            "rowGroup": {
                dataSrc: 'date',
                startRender: (!flat_view && searchParams == "" )? ( function ( rows, group ) {
                    return '<div>' + formatDate(group, 'JP') +' 追加<\/div>';
                    // enable rows count again when I find a way to show all rows in other pages
                    // return group +'更新 ('+rows.count()+'曲)';
                }) : null
            },
            "scrollX": true,

            initComplete: function () {
                var rows = this.api().rows().data();

                // Generate Filter dropdown per columns
                var table = this.api();
                table.columns().every(function () {
                    var order = table.order();
                    var column = this;
                    var column_data = column.data();
                    var column_param = columns_params[column.index()];

                    if (("filterable" in column_param) && (column_param.filterable == true)) {
                        var selectWrap = $('<div class="select-wrap"><span class="label">' + column_param.displayTitle + '</span></div>')
                            .appendTo($('.toolbar.filters'));
                        var select = $('<select id="' + column_param.name + '"><option value="" data-default>——</option></select>');

                        select.appendTo(selectWrap);

                        select.on('change', function () {
                            var val = $(this).val();
                            var val_e = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );

                            appendSelectboxStateClass($(this), val);

                            // var val = $(this).val();

                            // when applying filter, control rowgroup visibility
                            if (column.index() === 27 || (val_e === "" && order[0][0] === 27)) {
                                column.rowGroup().enable();
                                // console.log('group enabled (filter)');
                            } else {
                                column.rowGroup().disable();
                                // console.log('group disabled (filter active)');
                            }

                            // update URL params on change
                            updateQueryStringParameter(column_param.name, val);

                            column
                                .search(val_e ? '^' + val_e + '$' : '', true, false)
                                .draw();


                        });


                        // column parameter has customDropdownSortSource option
                        if (column_param.customDropdownSortSource) {
                            column_data = column_data.map(function (_, index) {
                                // get index of column
                                return index;
                            }).sort(function (index_a, index_b) {
                                // get index_a-th row and index_b-th row
                                var row_a = rows[index_a], row_b = rows[index_b];
                                // if customDropdownSortSource option is function type use it as comparator
                                if (typeof column_param.customDropdownSortSource === 'function') {
                                    return column_param.customDropdownSortSource(row_a, row_b);
                                    // if customDropdownSortSource option is string type use it as comparator column key
                                } else {
                                    return row_a[column_param.customDropdownSortSource].localeCompare(row_b[column_param.customDropdownSortSource])
                                }
                                // get column data again since we converted this array to row array in previous lines
                            }).map(function (index) {
                                // get index-th column's data
                                return column_data[index];
                            });
                        } else {
                            column_data = column_data.sort();
                        }

                        // reverse sort for date
                        if (column_param.reverseSortOrder) {
                            column_data.reverse();
                        }

                        // draw option list
                        column_data.unique().each(function (d, j) {
                            if (d != '') {
                                select.append('<option value="' + d + '">' + d + '</option>');
                            }
                        });

                        // set value for select on page init
                        if ('URLSearchParams' in window) {
                            var searchParamValue = searchParams.get(column_param.name);
                            if ( searchParamValue !== null ) {
                                var value = unescapeSlashes(searchParamValue)
                                column_data.unique().each(function (d) {
                                    select.val(value);
                                });
                                appendSelectboxStateClass(select, value);
                            }
                        }

                    }

                });

                // filter according to URL params on initial load
                if ('URLSearchParams' in window) {
                    searchParams.forEach(function (value, key) {
                        table.columns().every(function () {
                            var column = this;
                            var column_param = columns_params[column.index()];
                            var searchParamValue = searchParams.get(column_param.name);
                            var searchParamValue_e = $.fn.dataTable.util.escapeRegex(
                                decodeURIComponent(searchParamValue)
                            );

                            if ( searchParamValue !== null ) {
                                column.search(searchParamValue ? '^' + searchParamValue_e + '$' : '', true, false);
                            }
                        });
                    });

                    table.draw();
                }

                table.on('order.dt', function () {
                    var order = table.order();
                    var search = table.columns().search();
                    var searchActive = false;

                    for (let k = 0; k < search.length; k = k + 1) {
                        if (k in search && search[k] !== "") {
                            searchActive = true;
                            break;
                        }
                    }

                    // Disable rowgroup unless sorting by date
                    if (order[0][0] !== 27) {
                        table.rowGroup().disable();
                        // console.log('group disabled (sorting by non-date column)');
                        return;
                    }
                    // enable rowgroup if sorting by date AND search is inactive
                    else if ((order[0][0] === 27) && !searchActive) {
                        table.rowGroup().enable();
                        // console.log('group enabled (sorting by date + search inactive)');
                        return;
                    }
                    // do nothing
                    else {
                        // console.log('do nothing');
                        return;
                    }
                    table.draw();
                });

                $('#table').addClass('loading-done');
                $('html').removeClass('table-loading');

                // $('.column-toggle-bar').prepend('<span class="label">カラムON/OFF</span>');
            }
        });
    });

    
    // recalculate columns on colvis change event
    $('#table').on( 'column-visibility.dt', function () {
        $.fn.dataTable
            .tables( { visible: true, api: true } )
            .columns.adjust();
    } );

    $('select#chart_lev').on('change', function(){
        var table = $('#table').DataTable();
        var select = $(this);
        var val = $(this).val();
        var val_e = $.fn.dataTable.util.escapeRegex(
            $(this).val()
        );

        // simply filter if select is changed on /lv/ page
        if( select.data("type") == "filter") {
            table.column('chart_lev:name').search(val_e ? '^' + val_e + '$' : '', true, false);

            updateQueryStringParameter('chart_lev',val);

            table.draw();
        } 
        // redirect to /lv/ subpage with querystring if selected on main page
        else {
            window.location.href = './lv?chart_lev=' + encodeURIComponent(val);
        }
    });

    // update chart_lev selectbox value on page load
    if ('URLSearchParams' in window) {
        var searchParamValue = searchParams.get('chart_lev');
        if ( searchParamValue !== null ) {
            var value = unescapeSlashes(searchParamValue)
            $('select#chart_lev').val(value);
        }
    }

    $('button.reset-search').on('click', function(){
        var table = $('#table').DataTable();

        table
            .order(default_order) //FIXME: why doesn't work with just calling var?
            .search('')
            .columns().search('')
            .draw();

        clearQueryStringParameter();

        $('.toolbar.filters select').prop('selectedIndex',0).removeClass('changed');

        console.log('search reset');
    });

});