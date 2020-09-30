$(document).ready(function() {
    var columns_params = [
        { 
            displayTitle: "ID (system)",
            data: "id",
            className: "id",
            visible: false
        },
        { 
            displayTitle: "#",
            data: "image_url",
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
            data: "image_url",
            className: "jacket",
            render: function(data) {
                return '<span class="img-wrap"><img src=\"jacket/' + data.split(".")[0] + '.jpg\"\/><\/span><span class="index">' + data.split(".")[0] + '<\/span>';
            },
            width: "50px",
            orderable: false,
            searchable: false
        },
        { 
            displayTitle: "曲名",
            data: "title",
            className: "song-title",
            render: function ( data, type, row ) {
                // If display or filter data is requested, return title
                if ( type === 'display' ) {
                    return '<div class="inner-wrap"><span class="title">' + data + '<\/span><span class="artist-display hidden">' + row.artist + '<\/span><\/div>';
                }
                else if ( type === 'filter' ) {
                    return data;
                }
                // Else type detection or sorting data, return title_sort
                else {
                    return row.title_sort;
                }
            },
            width: "80vw",
        },
        {
            displayTitle: "曲名 (読み)",
            data: "title_sort",
            className: "title-sort",
            visible: false,
            searchable: false
        },
        { 
            // redundant (fake) merged title column for mobile
            displayTitle: "曲名・アーティスト",
            data: "title",
            className: "artist",
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
            data: "category",
            className: "category",
            render: renderInWrapper(),
            customDropdownSortSource: 'category_id',
            filterable: true
        },
        { 
            displayTitle: "ジャンルID",
            data: "category_id",
            width: "90px",
            visible: false
        },
        { 
            displayTitle: "チャプターID",
            data: "chap_id",
            className: "chapter-id",
            visible: false
        },
        {
            // combine chap_id + chapter
            displayTitle: "チャプター",
            data: function( row, type, set, meta ) {
                if (type === 'sort') {
                    return row.chap_id;
                } else {
                    row.chap_chapter = row.chap_id.substr(3,2);
                    if (row.chap_id.substr(0,1) == "0") {
                        // 01xxx : chapter 1
                        if (row.chap_id.substr(1,1) == "1") {
                            row.chap_book = "1";
                            row.chap_display = row.chap_book + '-' + row.chap_chapter + ' ' + row.chapter;
                            return row.chap_display;
                        } 
                        // 02xxx : chapter 2
                        else if (row.chap_id.substr(1,1) == "2") {
                            row.chap_book = "2";
                            row.chap_display = row.chap_book + '-' + row.chap_chapter + ' ' + row.chapter;
                            return row.chap_display;
                        }
                        // 03xxx : chapter 3
                        else if (row.chap_id.substr(1,1) == "3") {
                            // 0308x : chapter 3 side
                            if (row.chap_id.substr(0,4) == "0308") {
                                row.chap_book = "3";
                                row.chap_chapter = row.chap_id.substr(4,1);
                                row.chap_display = row.chap_book + '-S' + row.chap_chapter + ' ' + row.chapter;
                                return row.chap_display;
                            }
                            else {
                                row.chap_book = "3";
                                row.chap_display = row.chap_book + '-' + row.chap_chapter + ' ' + row.chapter;
                                return row.chap_display;
                            }
                        }
                        // 00xxx : default mylist
                        else {
                            row.chap_display = row.chapter;
                            return row.chap_display;
                        }
                    }
                    // 80xxx : Event chapters
                    else if (row.chap_id.substr(0,2) == "80") {
                        row.chap_book = "SP2";
                        row.chap_display = row.chap_book + '-' + row.chap_chapter + ' ' + row.chapter;
                        return row.chap_display;
                    }
                    // 99xxx : Event chapters
                    else if (row.chap_id.substr(0,2) == "99") {
                        row.chap_book = "SP";
                        row.chap_display = row.chap_book + '-' + row.chap_chapter + ' ' + row.chapter;
                        return row.chap_display;
                    }
                    // Others?
                    else {
                        row.chap_display = row.chap_id + ' ' + row.chapter;
                        return row.chap_display;
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
            data: "enemy_type",
            className: "type",
            render: function ( data, type, row ) {
                if ( type === 'display' ) {
                    return '<div class="inner-wrap"><span class="type-icon ' + data.toLowerCase() + '"><span>' + data + '<\/span><\/span></div>';
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
            data: "chara_id",
            visible: false
        },
        { 
            displayTitle: "相手キャラ",
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
            data: sortLevels('lev_bas', 'lev_bas_i'),
            className: "lv lv-bsc",
            render: renderLvNum('lev_bas', 'lev_bas_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_bas'),
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  ADVANCED
            displayTitle: "ADVANCED",
            data: sortLevels('lev_adv', 'lev_adv_i'),
            className: "lv lv-adv",
            render: renderLvNum('lev_adv', 'lev_adv_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_adv'),
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  EXPERT
            displayTitle: "EXPERT",
            data: sortLevels('lev_exc', 'lev_exc_i'),
            className: "lv lv-exp",
            render: renderLvNum('lev_exc', 'lev_exc_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_exc'),
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  MASTER
            displayTitle: "MASTER",
            data: sortLevels('lev_mas', 'lev_mas_i'),
            className: "lv lv-mas",
            render: renderLvNum('lev_mas', 'lev_mas_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_mas'),
            width: "3rem",
            filterable: flat_view ? false : true
        },
        { 
            //  LUNATIC
            displayTitle: "LUNATIC",
            data: sortLevels('lev_lnt', 'lev_lnt_i'),
            className: "lv lv-lnt",
            render: renderLvNum('lev_lnt', 'lev_lnt_i'),
            customDropdownSortSource: sortByLeadingZeros('lev_lnt'),
            width: "3rem",
            filterable: flat_view ? false : true
        },
        {
            //  chart_diff
            displayTitle: "譜面",
            data: ( flat_view ? 'chart_diff' : null ),
            className: "lv-name",
            width: "3rem",
            createdCell: flat_view ? ( function( td, cellData, rowData, row, col ) {
                $(td).addClass( rowData.chart_diff );
            }) : null,
            searchable: false,
            visible: false
        },
        {
            //  chart_lev (for sort)
            displayTitle: "難易度グループ",
            data: ( flat_view ? 'chart_lev' : null ),
            className: "lv",
            width: "4rem",
            customDropdownSortSource: sortByLeadingZeros('chart_lev'),
            filterable: flat_view,
            visible: false
        },
        {
            //  chart_lev_i
            displayTitle: "難易度",
            data: ( flat_view ? 'chart_lev_i' : null ),
            className: "lv lv-name",
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
            data: "new",
            searchable: false,
            visible: false
        },
        { 
            displayTitle: "追加日",
            data: "date",
            className: "date",
            filterable: true,
            render: renderInWrapper(),
            width: "4em"
        }
    ];

    var default_order = 
        flat_view ?
            [[21, 'desc']] :
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
                switch (row[chart_diff]) {
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

                return '<div class="inner-wrap"><span class="diff-name">' + chart_diff_display + '</span><span class="lv-num-wrap"><span class="lv-num-simple">' + row[simple_lv] + '<\/span><span class="lv-num-precise">' + row[precise_lv_display] + '<\/span></span><\/div>';
            }
            else {
                return data;
            }
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

    $.getJSON("data/music-ex.json", (data) => {
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

        var table = $('#table').DataTable( {
            // "ajax": {
            //     url: "data/music-ex.json",
            //     dataSrc: ""
            // },
            data: processed_data,
            "buttons": [
                {
                    extend: 'colvisRestore',
                    text: '全カラムON',
                },
                // {
                //     extend: 'colvisGroup',
                //     text: '全レベル ON',
                //     show: [ 14, 15, 16, 17, 18 ]
                // },
                {
                    extend: 'colvisGroup',
                    text: '譜面レベルのみ',
                    hide: [ 6, 8, 9, 10, 12, 13, 23 ],
                    show: [ 14, 15, 16, 17, 18 ],
                },
                {
                    extend: 'colvisGroup',
                    text: 'EXPERT以上のみ',
                    hide: [ 6, 8, 9, 10, 12, 13, 14, 15, 23 ],
                    show: [ 16, 17, 18 ]
                },
                // {
                //     extend: 'colvisGroup',
                //     className: 'asdf',
                //     text: 'ジャンル・チャプタ OFF',
                //     hide: [ 6, 9 ]
                // },
                {
                    extend: 'colvisGroup',
                    className: 'asdf',
                    text: '属性・Lv ON',
                    show: [ 10, 13 ]
                },
                {
                    extend: 'colvis',
                    className: 'config-btn',
                    columns: '.toggle',
                    text: 'カスタム設定',
                    collectionTitle: "表示・隠すカラムを選択",
                    collectionLayout: "fixed",
                    fade: 150
                },
            ],
            "columns": columns_params,
            "deferRender": true,
            "dom": '<"column-toggle-bar"B><"toolbar-group"<"toolbar filters"><"toolbar search"f>><"toolbar secondary"<"info"il>><"table-inner"rt><"paging"p>',
            "language": {
                "sEmptyTable":     "テーブルにデータがありません",
                "sInfo":           " _TOTAL_ 曲中 _START_〜_END_ まで表示中",
                "sInfoEmpty":      " 0 曲中 0〜0 まで表示中",
                "sInfoFiltered":   "（全 _MAX_ 曲）",
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
                            return data.title + '<br><span class="artist">' + data.artist + '<\/span>';
                        }
                    } ),
                    renderer: $.fn.dataTable.Responsive.renderer.tableAll()
                }
            },
            "rowGroup": {
                dataSrc: 'date',
                startRender: !flat_view ? ( function ( rows, group ) {
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
                        var select = $('<select><option value="" selected data-default>——</option></select>')
                            .appendTo(selectWrap)
                            .on('change', function () {
                                var val = $.fn.dataTable.util.escapeRegex(
                                    $(this).val()
                                );

                                // when applying filter, control rowgroup visibility
                                if (column.index() === 23 || (val === "" && order[0][0] === 23)) {
                                    column.rowGroup().enable();
                                    // console.log('group enabled (filter)');
                                } else {
                                    column.rowGroup().disable();
                                    // console.log('group disabled (filter active)');
                                }

                                column
                                    .search(val ? '^' + val + '$' : '', true, false)
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
                        if (column_param.data == 'date') {
                            column_data.reverse();
                        }

                        // draw option list
                        column_data.unique().each(function (d, j) {
                            if (d != '') {
                                select.append('<option value="' + d + '">' + d + '</option>');
                            }
                        });
                    }
                });

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

                $('.column-toggle-bar').prepend('<span class="label">カラムON/OFF</span>');
            }
        });
    });


    // table.on( 'search.dt', function () {
    //     console.log('search happened')
    // } );

    $('a.reset-search').on('click', function(){
        table
            .order([[23, 'desc'],[9, 'asc'],[0, 'asc']]) //FIXME: why doesn't work with just calling var?
            .search('')
            .columns().search('')
            .draw();

        $('.toolbar.filters select').prop('selectedIndex',0);

        console.log('search reset');
    });

});