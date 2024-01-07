const maimai_chart_list = {
    'lev_bas': 'BASIC',
    'dx_lev_bas': 'BASIC',
    'lev_adv': 'ADVANCED',
    'dx_lev_adv': 'ADVANCED',
    'lev_exp': 'EXPERT',
    'dx_lev_exp': 'EXPERT',
    'lev_mas': 'MASTER',
    'dx_lev_mas': 'MASTER',
    'lev_remas': 'Re:MASTER',
    'dx_lev_remas': 'Re:MASTER',
    'lev_utage': 'U·TA·GE',
};
var columns_params = [
    { 
        displayTitle: "ID (system)",
        name: "id",
        data: "sort",
        defaultContent: "",
        className: "id detail-hidden",
        visible: false
    },
    { 
        displayTitle: "#",
        name: "index",
        data: "id",
        defaultContent: "",
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
        defaultContent: "",
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
        defaultContent: "",
        className: "title-artist detail-hidden",
        render: function ( data, type, row ) {
            // If display or filter data is requested, return title
            if ( type === 'display' ) {
                return '<div class="inner-wrap">' +
                        '<span class="title">' + data + '<\/span>' +
                        '<span class="dash hidden"> - <\/span>' +
                        '<span class="artist-display hidden">' + row.artist + '<\/span>'+
                    '<\/div>';
            }
            else if ( type === 'filter' ) {
                return data;
            }
            // Else type detection or sorting data, return reading
            else {
                return row.reading;
            }
        },
        width: "80vw"
    },
    {
        displayTitle: "曲名 (読み)",
        name: "reading",
        data: "reading",
        defaultContent: "",
        className: "reading",
        visible: false,
        searchable: false
    },
    { 
        // Artist column (only on mobile - acts as title column on header)
        displayTitle: "アーティスト",
        name: "title_merged",
        data: "title",
        defaultContent: "",
        className: "artist detail-hidden",
        render: function ( data, type, row ) {
            // If display or filter data is requested, return title
            if ( type === 'display' ) {
                return '<div class="inner-wrap"><span class="artist-display hidden">' + row.artist + '<\/span><\/div>';
            }
            else {
                return row.reading;
            }
        },
        searchable: false
    },
    { 
        // hidden real artist column (for search)
        displayTitle: "アーティスト",
        name: "artist",
        data: "artist",
        defaultContent: "",
        className: "artist detail-hidden",
        visible: false
    },
    { 
        displayTitle: "BPM",
        name: "bpm",
        data: "bpm",
        defaultContent: "",
        className: "details bpm",
        searchable: false,
        visible: false
    },
    { 
        displayTitle: "バージョン",
        name: "version",
        data: maimaiRenderVersionName(),
        defaultContent: "",
        className: "details version",
        filterable: true,
        customDropdownSortSource: "version",
        width: "12em",
    },
    { 
        displayTitle: "ジャンル",
        name: "category",
        data: "catcode",
        defaultContent: "",
        className: "details category",
        render: renderInWrapper(),
        width: "12em",
        filterable: true,
    },
    { 
        //  Chart type
        displayTitle: "DX/Std",
        name: "chart_type",
        data: maimaiGetChartTypes(),
        defaultContent: "",
        className: "chart-type",
        render: maimaiRenderChartTypeBadges(),
        // customDropdownSortSource: sortByLeadingZeros('lev_bas'),
        // reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  BASIC
        displayTitle: "BASIC",
        name: "lev_bas",
        data: maimaiProcessLvData('lev_bas', 'lev_bas_i'),
        defaultContent: "",
        className: "lv lv-bsc",
        render: maimaiRenderLvNum('lev_bas'),
        customDropdownSortSource: sortByLeadingZeros('lev_bas'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  ADVANCED
        displayTitle: "ADVANCED",
        name: "lev_adv",
        data: maimaiProcessLvData('lev_adv', 'lev_adv_i'),
        defaultContent: "",
        className: "lv lv-adv",
        render: maimaiRenderLvNum('lev_adv'),
        customDropdownSortSource: sortByLeadingZeros('lev_adv'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  EXPERT
        displayTitle: "EXPERT",
        name: "lev_exp",
        data: maimaiProcessLvData('lev_exp', 'lev_exp_i'),
        defaultContent: "",
        className: "lv lv-exp",
        render: maimaiRenderLvNum('lev_exp'),
        customDropdownSortSource: sortByLeadingZeros('lev_exp'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  MASTER
        displayTitle: "MASTER",
        name: "lev_mas",
        data: maimaiProcessLvData('lev_mas', 'lev_mas_i'),
        defaultContent: "",
        className: "lv lv-mas",
        render: maimaiRenderLvNum('lev_mas'),
        customDropdownSortSource: sortByLeadingZeros('lev_mas'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  Re:MASTER
        displayTitle: "Re:MASTER",
        name: "lev_remas",
        data: maimaiProcessLvData('lev_remas', 'lev_remas_i'),
        defaultContent: "",
        className: "lv lv-remas",
        render: maimaiRenderLvNum('lev_remas'),
        customDropdownSortSource: sortByLeadingZeros('lev_remas'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  UTAGE (Kanji)
        displayTitle: "UTAGE (Kanji)",
        name: "lev_utage",
        data: "kanji",
        defaultContent: "",
        className: "lv lv-utage kanji",
        render: renderUtage('kanji', 'lev_utage'),
        // customDropdownSortSource: ( function(data) { data ? sortByLeadingZeros('lev_utage') : null }),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
    },
    { 
        //  UTAGE
        displayTitle: "UTAGE",
        name: "lev_utage",
        data: "lev_utage",
        defaultContent: "",
        className: "lv lv-utage",
        customDropdownSortSource: sortByLeadingZeros('lev_utage'),
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
                        return convertDifficultyNames(row.chart_diff, false, maimai_chart_list);
                    }
                } else {
                    return null;
                }
            },
        defaultContent: "",
        className: "lv-name detail-hidden",
        width: "3rem",
        createdCell: flat_view ? ( function( td, cellData, rowData, row, col ) {
            $(td).addClass( rowData.chart_diff );
        }) : null,
        render: flat_view ? renderChartDifficultyName('chart_diff',false,maimai_chart_list) : null,
        customDropdownSortSource: flat_view ? sortByDifficultyCategory('chart_diff', maimai_chart_list) : null,
        filterable: flat_view,
        visible: false
    },
    {
        //  chart_lev (for sort)
        displayTitle: "難易度グループ",
        name: "chart_lev",
        data: ( flat_view ? 'chart_lev' : null ),
        defaultContent: "",
        className: "lv detail-hidden",
        width: "4rem",
        customDropdownSortSource: ( function(data) { data ? sortByLeadingZeros('chart_lev') : null }),
        reverseSortOrder: true,
        visible: false
    },
    {
        //  chart_lev_i
        displayTitle: "譜面レベル",
        name: "chart_lev_i",
        data: ( flat_view ? 'chart_lev_i' : null ),
        defaultContent: "",
        className: "lv lv-name detail-hidden",
        render: ( flat_view ? renderChartDifficultyNameAndLv('chart_diff', 'chart_lev', 'chart_lev_i', 'chart_lev_i_display', maimai_chart_list) : null),
        width: "4rem",
        createdCell: flat_view ? ( function( td, cellData, rowData, row, col ) {
            $(td).addClass( rowData.chart_diff );
        }) : null,
        searchable: false,
        visible: flat_view
    },
    { 
        displayTitle: "ノート数",
        name: "chart_notes",
        data: ( flat_view ? "chart_notes" : null ),
        defaultContent: "",
        className: "details notecount detail-hidden nowrap",
        width: "8em",
        searchable: false
    },
    { 
        displayTitle: "TAP",
        name: "chart_notes_tap",
        data: ( flat_view ? "chart_notes_tap" : null ),
        defaultContent: "",
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
    },
    { 
        displayTitle: "HOLD",
        name: "chart_notes_hold",
        data: ( flat_view ? "chart_notes_hold" : null ),
        defaultContent: "",
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
    },
    { 
        displayTitle: "SLIDE",
        name: "chart_notes_slide",
        data: ( flat_view ? "chart_notes_slide" : null ),
        defaultContent: "",
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
    },
    { 
        displayTitle: "TOUCH",
        name: "chart_notes_touch",
        data: ( flat_view ? "chart_notes_touch" : null ),
        defaultContent: "",
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
    },
    { 
        displayTitle: "BREAK",
        name: "chart_notes_break",
        data: ( flat_view ? "chart_notes_break" : null ),
        defaultContent: "",
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
    },
    { 
        displayTitle: "譜面作者",
        name: "chart_designer",
        data: ( flat_view ? "chart_designer" : null ),
        defaultContent: "",
        width: "15em",
        className: "details detail-hidden designer",
        filterable: flat_view,
        searchable: flat_view
    },
    { 
        displayTitle: "譜面作者",
        name: "chart_link",
        data: ( flat_view ? "chart_link" : null ),
        defaultContent: "",
        render: ( flat_view ? renderChartLinkBtn('chart_link') : null ),
        width: "5em",
        className: "details detail-hidden chart-link",
    },
    { 
        displayTitle: "追加日",
        name: "date",
        defaultContent: "",
        data: function( row, type, set, meta ) {
            return formatDate(row.release)
        },
        className: "date",
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
        width: "4em",
        filterable: true
    },
    { 
        displayTitle: "NEW",
        name: "new",
        data: "newflag",
        defaultContent: "",
        className: "detail-hidden", // this column is required to ensure modal displays
        searchable: false
    }
];

var default_order = 
    flat_view ?
        // 難易度 , Lv , Date
        [[getColumnIndexByName('chart_lev'), 'desc'],[getColumnIndexByName('chart_diff'), 'desc'],[getColumnIndexByName('date'), 'desc']] :
        // date , ID
        [[getColumnIndexByName('date'), 'desc'],[getColumnIndexByName('id'), 'asc']];


function maimaiGetChartTypes() {
    return function(row, data) {
        let lev = `lev_bas`;
        let dx_lev = `dx_lev_bas`;

        // only DX chart
        if (row[dx_lev] && !row[lev]) {
            return 'DX';
        } 

        // only Std chart
        if (row[lev] && !row[dx_lev]) {
            return 'Std';
        }

        // both
        if (row[dx_lev] && row[lev]) {
            return 'DX & Std';
        }

        // UTAGE
        if (row['kanji']) {
            return 'UTAGE';
        }
    }
}

function maimaiRenderChartTypeBadges() {
    return function(data, type, row) {
        if ( type === 'display') {

            if (flat_view) {
                if (row['chart_diff'].startsWith("dx_")) {
                    var dx_lev = row['chart_diff'];
                } else {
                    var lev = row['chart_diff'];
                }
            } else {
                var lev = `lev_bas`;
                var dx_lev = `dx_lev_bas`;
            }
            var dx_badge = '';
            var std_badge = '';
            var utage_badge = ''; 

            // only DX chart
            if (row[dx_lev]) {
                var dx_badge = `<span class="chart-type-badge dx"></span>`;
            } 

            // only Std chart
            if (row[lev]) {
                var std_badge = `<span class="chart-type-badge std"></span>`;
            }

            // UTAGE
            // if (row['kanji']) {
            //     var utage_badge = `<span class="chart-type-badge utage"></span>`;
            // }

            return `<div class="inner-wrap">${dx_badge}${std_badge}</div>`;
        } else {
            return data;
        }
    }
}

function maimaiProcessLvData(lev, lev_i) {
    return function(row, data) {
        let dx_lev = `dx_${lev}`;
        let dx_lev_i = `dx_${lev_i}`;

        // only DX chart
        if (row[dx_lev] && !row[lev]) {
            // constant exists
            return row[dx_lev];
        } 

        // only Std chart
        if (row[lev] && !row[dx_lev]) {
            // constant exists
            return row[lev];
        }

        // both
        if (row[dx_lev] && row[lev]) {
            // constant exists
            return row[dx_lev];
        }
    }
}

function maimaiRenderLvNum(lev) {
    return function ( data, type, row ) {
        if ( type === 'display') {
            var lev_i = `${lev}_i`; // lev_bas_i
            var dx_lev = `dx_${lev}`; // dx_lev_bas
            var dx_lev_i = `dx_${lev_i}`;
            
            var primary_lev = '';
            var primary_chart_type = '';

            // only DX chart
            if (row[dx_lev] && !row[lev]) {
                var primary_chart_type = 'DX';
                var primary_lev = row[dx_lev];
                var primary_lev_i = row[dx_lev_i];
            } 

            // only Std chart
            if (row[lev] && !row[dx_lev]) {
                var primary_chart_type = 'Std';
                var primary_lev = row[lev];
                var primary_lev_i = row[lev_i];
            }

            // TODO: HANDLE DUAL TYPE DISPLAY
            // both
            if (row[dx_lev] && row[lev]) {
                var primary_chart_type = 'DX';
                var primary_lev = row[dx_lev];
                var primary_lev_i = row[dx_lev_i];
                var secondary_chart_type = 'Std';
                var secondary_lev = row[lev];
                var secondary_lev_i = row[lev_i];
            }

            function maimaiLvNumHtmlTemplate(chart_type, cur_lev, cur_lev_i) {
                var lev_i_html = (cur_lev_i ? `<span class="lv-num-precise">${cur_lev_i}</span>` : '')

                // Find if + exists in lv number
                var match = cur_lev.match(/^([0-9]{1,2})(\+)?$/);
                var lev_num_html = (match ? `<span class="num">${match[1]}</span>` : cur_lev);
                var plus_html = ( match && match[2] === '+' ? '<span class="plus">+</span>' : '');

                return `<span class="chart-type-label">${chart_type}</span>
                        <span class="lv-num-simple">${lev_num_html}${plus_html}</span>
                        ${lev_i_html}`
            }
            
            if (row[dx_lev] && row[lev]) {
                return `
                    <div class="inner-wrap">
                        <div class="primary">${maimaiLvNumHtmlTemplate(primary_chart_type, primary_lev, primary_lev_i)}</div>
                        <div class="secondary">${maimaiLvNumHtmlTemplate(secondary_chart_type, secondary_lev, secondary_lev_i)}</div>
                    </div>`;
            } else if (row[lev] && lev === 'lev_remas' && row['dx_lev_mas'] || row[dx_lev] && dx_lev === 'dx_lev_remas' && row['lev_mas'] ) {
                // Re:MAS when there is DX chart
                return `
                    <div class="inner-wrap ${ lev === 'dx_lev_remas' ? 'reverse' : '' }">
                        <div class="primary empty">${maimaiLvNumHtmlTemplate('--', '--', '')}</div>
                        <div class="secondary">${maimaiLvNumHtmlTemplate(primary_chart_type, primary_lev, primary_lev_i)}</div>
                    </div>`;
            } else {
                return `
                    <div class="inner-wrap">
                        <div class="primary ${ primary_lev === '' ? 'empty' : '' }">${maimaiLvNumHtmlTemplate(primary_chart_type, primary_lev, primary_lev_i)}</div>
                    </div>`;
            }
        }
        else {
            return data;
        }
    }
}

function renderUtage(kanji, lev_utage) {
    return function ( data, type, row ) {
        if ( type === 'display' ) {
            var html_output = `
                <div class="inner-wrap">
                    <div class="primary">
                        <span class="lv-num-simple">${row[kanji]}</span>
                        <span class="lv-num-precise">${row[lev_utage]}</span>
                    </div>
                </div>`;
            return row[kanji] ? html_output : '';
        }
        else {
            return data;
        }
    }
}

function maimaiProcessChartData(obj, chart_diff) {
    if (obj[chart_diff]) {
        if (chart_diff === 'kanji') {
            return {
                ...obj,
                chart_diff,
                chart_lev: obj[chart_diff],
                chart_lev_i: obj[`lev_utage`],
                chart_lev_i_display: obj[`lev_utage`],
                chart_notes: obj[`lev_utage_notes`],
                chart_notes_tap: obj[`lev_utage_notes_tap`],
                chart_notes_hold: obj[`lev_utage_notes_hold`],
                chart_notes_slide: obj[`lev_utage_notes_slide`],
                chart_notes_touch: obj[`lev_utage_notes_touch`],
                chart_notes_break: obj[`lev_utage_notes_break`],
                chart_designer: obj[`lev_utage_designer`],
                chart_link: obj[`lev_utage_chart_link`]
            }
        }
        else {
            return {
                ...obj,
                chart_diff,
                chart_lev: obj[chart_diff],
                chart_lev_i: parseFloat(obj[`${chart_diff}_i`] || obj[chart_diff].replace('+', '.5')),
                chart_lev_i_display: obj[`${chart_diff}_i`] || `<span class="approx">${parseFloat(obj[chart_diff].replace('+', '.5')).toFixed(1)}</span>`,
                chart_notes: obj[`${chart_diff}_notes`],
                chart_notes_tap: obj[`${chart_diff}_notes_tap`],
                chart_notes_hold: obj[`${chart_diff}_notes_hold`],
                chart_notes_slide: obj[`${chart_diff}_notes_slide`],
                chart_notes_touch: obj[`${chart_diff}_notes_touch`],
                chart_notes_break: obj[`${chart_diff}_notes_break`],
                chart_designer: obj[`${chart_diff}_designer`],
                chart_link: obj[`${chart_diff}_chart_link`]
            };
        }
    }
    return null;
}

function maimaiRenderVersionName() {
    return function( row, type, set, meta ) {
        if ( type === 'sort' || type === 'meta') {
            return row.version;
        } else {
            const version_list = {
                "10000": "maimai",
                "11000": "maimai PLUS",
                "12000": "GreeN",
                "13000": "GreeN PLUS",
                "14000": "ORANGE",
                "15000": "ORANGE PLUS",
                "16000": "PiNK",
                "17000": "PiNK PLUS",
                "18000": "MURASAKi",
                "18500": "MURASAKi PLUS",
                "19000": "MiLK",
                "19500": "MiLK PLUS",
                "19900": "FiNALE",
                "20000": "でらっくす",
                "20500": "でらっくす PLUS",
                "21000": "Splash",
                "21500": "Splash PLUS",
                "22000": "UNiVERSE",
                "22500": "UNiVERSE PLUS",
                "23000": "FESTiVAL",
                "23500": "FESTiVAL PLUS",
                "24000": "BUDDiES"
            };

            let closestVersion = null;

            for (const versionNumber in version_list) {
                if (row['version'] >= versionNumber && (closestVersion === null || versionNumber > closestVersion)) {
                    closestVersion = versionNumber;
                }
            }

            return version_list[closestVersion];
        }
    }
}

$(document).ready(function() {
    $.getJSON("data/music-ex.json", (data) => {
        var table = $('#table').DataTable( {
            // "ajax": {
            //     url: "data/music-ex.json",
            //     dataSrc: ""
            // },
            data: flattenMusicData(data, flat_view, maimai_chart_list, maimaiProcessChartData),
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
                "searchPlaceholder": "曲名・アーティスト",
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
                            var wiki_url_guess = 'https:\/\/gamerch.com\/maimai\/search?q=' + encoded_title;

                            var wiki_url = data['wiki_url'] ? data['wiki_url'] : wiki_url_guess;


                            return '<div class="modal-header" style="--img:url(jacket/' + data.image_url + ');"><span class="header-img"></span><span class="header-img-overlay"></span><div class="img-wrap">' + 
                                '<img src=\"jacket/' + data.image_url + '\"\/>' +
                                '<\/div><div class="content-wrap">' +
                                '<span class="title">' + data.title + '<\/span>' +
                                '<span class="artist">' + data.artist + '<\/span>' +
                                '<div class="quicklinks">' +
                                '<a class="wiki" href="' + wiki_url + '" target="_blank" rel="noopener noreferer nofollow">Wiki<\/a>' +
                                '<a class="youtube" href="https:\/\/youtube.com\/results?search_query=maimai+譜面確認+' + encoded_title + '" target="_blank" rel="noopener noreferer nofollow"><\/a>' +
                                '<\/div>' +
                                '<\/div><\/div>'
                        },
                        footer: function ( row ) {
                            var data = row.data();
                            return '<div class="modal-footer">' +
                                '<div class="report"><a class="report-btn" href="https:\/\/twitter.com\/intent\/tweet?text=@zvuc_%0A%E3%80%90%23maimai_DB%20%E6%83%85%E5%A0%B1%E6%8F%90%E4%BE%9B%E3%80%91%0A%E6%9B%B2%E5%90%8D%EF%BC%9A' + encodeURIComponent(data.title) +'%0A%E8%AD%9C%E9%9D%A2%EF%BC%9A" target="_blank" rel="noopener noreferer nofollow">💬 足りない情報・間違いを報告する （Twitter）<\/a><\/div>' +
                                '<\/div>'
                        }
                    } ),
                    // renderer: $.fn.dataTable.Responsive.renderer.tableAll()
                    renderer: function(api, rowIdx, columns) {

                        var row = api.row(rowIdx);
                        var data = row.data();
                        var utage = data['kanji'] !== "" ? "utage" : "";

                        var normalRows = $.map(columns, function(col, i) {
                            var column_param = columns_params[col.columnIndex];

                            // generic
                            if (!col.className.includes('detail-hidden') && !col.className.includes('lv ')) {
                                return '<div class="row ' + col.className + '" data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                                '<span class="row-label">' + col.title + '</span> ' + '<span>' + col.data + '</span>' +
                                '</div>'
                            }
                        }).join('');

                        var chartRows = $.map(columns, function(col, i) {
                            var column_param = columns_params[col.columnIndex];

                            // lv display
                            if (!col.className.includes('detail-hidden') && col.className.includes('lv ')) {
                                console.log(column_param['name']);
                                var chart_name = column_param['name'];

                                var notes = chart_name.concat('_notes');
                                var notes_tap = chart_name.concat('_notes_tap');
                                var notes_hold = chart_name.concat('_notes_hold');
                                var notes_slide = chart_name.concat('_notes_slide');
                                var notes_touch = chart_name.concat('_notes_touch');
                                var notes_break = chart_name.concat('_notes_break');

                                var designer = chart_name.concat('_designer');
                                var chart_link = chart_name.concat('_chart_link');                                

                                return '<div class="row ' + col.className + '" data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                                    '<span class="row-label"><span>' + column_param.displayTitle + '</span></span> ' + 
                                    '<span class="content-col">' +
                                        '<span class="main-info-wrap">' + (utage ? ('<div class="inner-wrap"><span class="lv-num-simple">' + data['kanji'] + '</span><span class="lv-num-precise">' + data['lev_utage'] + '</span></div>') : col.data) + '</span>' +
                                        '<span class="sub-info-wrap">' +
                                            ( hasPropertyAndValue(data, notes) ? '<span class="notes-detail-wrap"><span class="notes"><span class="label">Notes</span><span>' + data[notes] + '</span></span><span class="notes-sub-detail-wrap">' +
                                                ( hasPropertyAndValue(data, notes_tap) ? '<span class="notes_tap"><span class="label">tap</span><span>' + data[notes_tap] + '</span></span>' : "") +
                                                ( hasPropertyAndValue(data, notes_hold) ? '<span class="notes_hold"><span class="label">hold</span><span>' + data[notes_hold] + '</span></span>' : "") +
                                                ( hasPropertyAndValue(data, notes_slide) ? '<span class="notes_slide"><span class="label">slide</span><span>' + data[notes_slide] + '</span></span>' : "") +
                                                ( hasPropertyAndValue(data, notes_touch) ? '<span class="notes_touch"><span class="label">air</span><span>' + data[notes_touch] + '</span></span>' : "") +
                                                ( hasPropertyAndValue(data, notes_break) ? '<span class="notes_break"><span class="label">flick</span><span>' + data[notes_break] + '</span></span>' : "") + '</span></span>' : "") +
                                            ( hasPropertyAndValue(data, designer) ? '<span class="designer"><span class="label">Designer</span><span>' + data[designer] + '</span></span>' : "") +
                                        '</span>' +
                                    '</span>' +
                                    ( hasPropertyAndValue(data, chart_link) ? '<span class="chart-link">' + chartLinkBtn(data[chart_link]) + '</span>' : "") +
                                    '</div>'
                            }
                        }).join('');

                        var combinedRows = $('<div class="table-wrapper"/>')
                                                .append(
                                                    $('<div class="details-table chart-details '+ utage + '"/>')
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
                dataSrc: 'release',
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