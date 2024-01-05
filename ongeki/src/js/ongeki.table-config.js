const ongeki_chart_list = {
    'lev_bas': 'BASIC',
    'lev_adv': 'ADVANCED',
    'lev_exc': 'EXPERT',
    'lev_mas': 'MASTER',
    'lev_lnt': 'LUNATIC'
};
var columns_params = [
    { 
        displayTitle: "ID (system)",
        name: "id",
        data: "id",
        className: "id detail-hidden",
        visible: false,
        searchable: false
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
        className: "title-artist detail-hidden",
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
        // Artist column (only on mobile - acts as title column on header)
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
    },
    { 
        // hidden real artist column (for search)
        displayTitle: "アーティスト",
        name: "artist",
        data: "artist",
        className: "artist detail-hidden",
        visible: false
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
        className: "details category",
        render: renderInWrapper(),
        customDropdownSortSource: 'category_id',
        filterable: true
    },
    { 
        displayTitle: "ジャンルID",
        name: "category_id",
        data: "category_id",
        width: "90px",
        visible: false,
        searchable: false
    },
    { 
        displayTitle: "チャプターID",
        name: "chap_id",
        data: "chap_id",
        className: "chapter-id",
        visible: false,
        searchable: false
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
        filterable: true,
        visible: false
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
        filterable: true,
    },
    { 
        displayTitle: "キャラID",
        name: "chara_id",
        data: "chara_id",
        visible: false,
        searchable: false
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
        width: "4em",
        searchable: false
    },
    { 
        //  BASIC
        displayTitle: "BASIC",
        name: "lev_bas",
        data: sortLevels('lev_bas'),
        className: "lv lv-bsc",
        render: renderLvNum('lev_bas'),
        customDropdownSortSource: sortByLeadingZeros('lev_bas'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true
    },
    { 
        //  ADVANCED
        displayTitle: "ADVANCED",
        name: "lev_adv",
        data: sortLevels('lev_adv'),
        className: "lv lv-adv",
        render: renderLvNum('lev_adv'),
        customDropdownSortSource: sortByLeadingZeros('lev_adv'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  EXPERT
        displayTitle: "EXPERT",
        name: "lev_exc",
        data: sortLevels('lev_exc'),
        className: "lv lv-exp",
        render: renderLvNum('lev_exc'),
        customDropdownSortSource: sortByLeadingZeros('lev_exc'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  MASTER
        displayTitle: "MASTER",
        name: "lev_mas",
        data: sortLevels('lev_mas'),
        className: "lv lv-mas",
        render: renderLvNum('lev_mas'),
        customDropdownSortSource: sortByLeadingZeros('lev_mas'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  LUNATIC
        displayTitle: "LUNATIC",
        name: "lev_lnt",
        data: sortLevels('lev_lnt'),
        className: "lv lv-lnt",
        render: renderLvNum('lev_lnt'),
        customDropdownSortSource: sortByLeadingZeros('lev_lnt'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
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
                        return convertDifficultyNames(row.chart_diff, false, ongeki_chart_list);
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
        render: flat_view ? renderChartDifficultyName('chart_diff', false, ongeki_chart_list) : null,
        customDropdownSortSource: flat_view ? sortByDifficultyCategory('chart_diff', ongeki_chart_list) : null,
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
        visible: false
    },
    {
        //  chart_lev_i
        displayTitle: "譜面レベル",
        name: "chart_lev_i",
        data: ( flat_view ? 'chart_lev_i' : null ),
        className: "lv lv-name detail-hidden",
        render: ( flat_view ? renderChartDifficultyNameAndLv('chart_diff', 'chart_lev', 'chart_lev_i', 'chart_lev_i_display', ongeki_chart_list)
        : null ),
        width: "4rem",
        createdCell: flat_view ? ( function( td, cellData, rowData, row, col ) {
            $(td).addClass( rowData.chart_diff );
        }) : null,
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
        width: "10px",
        searchable: false
    }
];

var default_order = 
    flat_view ?
        // 難易度 , Lv , Date
        [[getColumnIndexByName('chart_lev_i'), 'desc'],[getColumnIndexByName('chart_diff'), 'desc'],[getColumnIndexByName('date'), 'desc']] :
        // date , ID
        [[getColumnIndexByName('date'), 'desc'],[getColumnIndexByName('id'), 'asc']];

function processOngekiChartData(obj, chart_diff) {
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

$(document).ready(function() {
    $.getJSON("data/music-ex.json", (data) => {
        var table = $('#table').DataTable( {
            // "ajax": {
            //     url: "data/music-ex.json",
            //     dataSrc: ""
            // },
            data: flattenMusicData(data, flat_view, ongeki_chart_list, processOngekiChartData),
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
                "emptyTable":     "テーブルにデータがありません",
                "info":           replaceUnitText(" _TOTAL_unit (_START_〜_END_ 表示中)"),
                "infoEmpty":      replaceUnitText(" 0 unit"),
                "infoFiltered":   replaceUnitText("（全 _MAX_ unit）"),
                "infoPostFix":    "",
                "infoThousands":  ",",
                "lengthMenu":     "1ページ表示 _MENU_",
                "loadingRecords": "読み込み中...",
                "processing":     "処理中...",
                "search":         "検索",
                "searchPlaceholder": "曲名・アーティスト・キャラ",
                "zeroRecords":    "一致するレコードがありません",
                "paginate": {
                    "sFirst":    "先頭",
                    "sLast":     "最終",
                    "sNext":     "NEXT",
                    "sPrevious": "PREV"
                },
                "aria": {
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
            initComplete: function() {
                var table = this;
                tableInitCompleteFunctions(table);
            }
        });
    });
});