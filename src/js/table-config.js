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
            data: "image_url detail-hidden",
            className: "id",
            data: function(row) {
                return row.image_url.split(".")[0];
            },
            render: renderInWrapper(),
            width: "20px",
            searchable: false
        },
        { 
            displayTitle: "アルバムアート",
            name: "jacket",
            data: "image_url",
            className: "jacket detail-hidden",
            render: function(data) {
                return '<span class="img-wrap"><img src=\"jacket/' + data.split(".")[0] + '.jpg\"\/><\/span><span class="index">' + data.split(".")[0] + '<\/span>';
            },
            width: "50px",
            orderable: false,
            searchable: false
        },
        { 
            displayTitle: "曲名",
            name: "title",
            data: "title",
            className: "song-title",
            render: function ( data, type, row ) {
                // If display or filter data is requested, return title
                if ( type === 'display' ) {
                    return '<div class="inner-wrap">' +
                            ( row.bonus == "1" ? '<span class="bonus">BONUS<\/span>' : "") +
                            '<span class="title">' + data + '<\/span>' +
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
            displayTitle: "曲名・アーティスト",
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
                            return chap_book + '-' + chap_chapter + ' ' + row.chapter;
                        } 
                        // 00xxx : default mylist
                        else {
                            return row.chapter;
                        }
                    }
                    // 80xxx : Event chapters
                    else if (chap_id.substr(0,2) == "80") {
                        var chap_book = "SP2";
                        return chap_book + '-' + chap_chapter + ' ' + row.chapter;
                    }
                    // 99xxx : Event chapters
                    else if (chap_id.substr(0,2) == "99") {
                        var chap_book = "SP";
                        return chap_book + '-' + chap_chapter + ' ' + row.chapter;
                    }
                    // Others?
                    else {
                        chap_display = chap_id + ' ' + row.chapter;
                        return chap_display;
                    }
                }
            },
            className: "chapter",
            width: "15em",
            render: renderInWrapper(),
            filterable: true
        },
        { 
            displayTitle: "属性",
            name: "enemy_type",
            data: "enemy_type",
            className: "type",
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
            className: "character",
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
            className: "enemy-lv",
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
                            console.log(row.chart_diff);
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
            displayTitle: "追加日",
            name: "date",
            data: "date",
            className: "date",
            filterable: true,
            render: renderInWrapper(),
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
            [[21, 'desc'],[13, 'desc'],[23, 'desc']] :
            [[23, 'desc'],[9, 'asc'],[0, 'asc']];
    
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
        const processed_data =
            ( flat_view ? (
                data
                    .map(obj =>
                        ['lev_bas', 'lev_adv', 'lev_exc', 'lev_mas', 'lev_lnt']
                            .map(chart_diff =>
                                obj[chart_diff]
                                    ? {
                                        ...obj,
                                        chart_diff,
                                        chart_lev: obj[chart_diff],
                                        chart_lev_i: parseFloat(obj[`${chart_diff}_i`] || obj[chart_diff].replace('+', '.7')),
                                        chart_lev_i_display: obj[`${chart_diff}_i`] || '<span class="approx">' + parseFloat(obj[chart_diff].replace('+', '.7')).toFixed(1) + '</span>'
                                    }
                                    : null
                            )
                    )
                    .flat()
                    .filter(obj => !!obj)
                )
                : data 
            );
        return processed_data;
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
                //     hide: [ 6, 8, 9, 10, 12, 13, 23 ],
                //     show: [ 14, 15, 16, 17, 18 ],
                // },
                // {
                //     extend: 'colvisGroup',
                //     text: 'EXPERT以上のみ',
                //     hide: [ 6, 8, 9, 10, 12, 13, 14, 15, 23 ],
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
                            return '<div class="modal-header"><div class="img-wrap">' + 
                                '<img src=\"jacket/' + data.image_url.split(".")[0] + '.jpg\"\/>' +
                                '<\/div><div class="content-wrap">' +
                                ( data.bonus == "1" ? '<span class="bonus">BONUS<\/span>' : "") +
                                '<span class="title">' + data.title + '<\/span>' +
                                '<span class="artist">' + data.artist + '<\/span><\/div><\/div>'
                        },
                        footer: function ( row ) {
                            var data = row.data();
                            return '<div class="modal-footer">' +
                                ( data.copyright1 !== "-" ? '<span class="copyright">' + data.copyright1.replace(/\s+ピアプロロゴ/, '<span class="piapro">piapro</span>') + '<\/span>' : '' ) +
                                '<\/div>'
                        }
                    } ),
                    renderer: $.fn.dataTable.Responsive.renderer.tableAll()
                }
            },
            "rowGroup": {
                dataSrc: 'date',
                startRender: (!flat_view && searchParams == "" )? ( function ( rows, group ) {
                    return '<div>' + group +' 追加<\/div>';
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
                            if (column.index() === 23 || (val_e === "" && order[0][0] === 23)) {
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

                    // console.log('Reorder happened!');
                    // console.log(order);

                    for (let k = 0; k < search.length; k = k + 1) {
                        if (k in search && search[k] !== "") {
                            searchActive = true;
                            // console.log(searchActive);
                            break;
                        }
                    }

                    // Disable rowgroup unless sorting by date
                    if (order[0][0] !== 23) {
                        table.rowGroup().disable();
                        // console.log('group disabled (sorting by non-date column)');
                        return;
                    }
                    // enable rowgroup if sorting by date AND search is inactive
                    else if ((order[0][0] === 23) && !searchActive) {
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


    // table.on( 'search.dt', function () {
    //     console.log('search happened')
    // } );

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
            window.location.href = '/lv?chart_lev=' + encodeURIComponent(val);
        }

        // select.val(String(val));

        // console.log(val);
    });

    // update chart_lev selectbox value on page load
    if ('URLSearchParams' in window) {
        var searchParamValue = searchParams.get('chart_lev');
        if ( searchParamValue !== null ) {
            var value = unescapeSlashes(searchParamValue)
            $('select#chart_lev').val(value);
        }
    }

    $('a.reset-search').on('click', function(){
        var table = $('#table').DataTable();

        table
            .order(default_order) //FIXME: why doesn't work with just calling var?
            .search('')
            .columns().search('')
            .draw();

        clearQueryStringParameter();

        $('.toolbar.filters select').prop('selectedIndex',0);

        console.log('search reset');
    });

});