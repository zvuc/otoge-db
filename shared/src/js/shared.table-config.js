var searchParams = new URLSearchParams(window.location.search);

function hasPropertyAndValue(json, property) {
    return json.hasOwnProperty(property) && json[property] !== "";
}

function sortLevels(lev) {
    return function ( row, type, set, meta ) {
        var lev_i = `${lev}_i`;

        if ( type === 'sort' ) {
            if (row[lev_i]) {
                return addLeadingZero(row[lev_i]);
            } else {
                return addLeadingZero(row[lev]);
            }
        }
        else {
            return row[lev];
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
        var a = ( row_a[column] ? row_a[column] : '')
        var b = ( row_b[column] ? row_b[column] : '')
        return addLeadingZero(a).localeCompare(addLeadingZero(b));
    }
}

function renderLvNum(lev) {
    return function ( data, type, row ) {
        if ( type === 'display' && row[lev]) {
            var lev_i = `${lev}_i`;
            var lev_i_html = (row[lev_i] ? `<span class="lv-num-precise">${row[lev_i]}</span>` : '')

            // Find if + exists in lv number
            var match = row[lev].match(/^([0-9]{1,2})(\+)?$/);
            var lev_num_html = (match ? `<span class="num">${match[1]}</span>` : row[lev]);
            var plus_html = (match[2] === '+' ? '<span class="plus">+</span>' : '');
            
            return `<div class="inner-wrap"><span class="lv-num-simple">${lev_num_html}${plus_html}</span>${lev_i_html}</div>`;
        }
        else {
            return data;
        }
    }
}

function renderChartDifficultyNameAndLv(chart_diff, simple_lv, precise_lv, precise_lv_display, chart_link) {
    return function ( data, type, row ) {
        if ( type === 'display' ) {
            var chart_diff_display = convertDifficultyNames(row[chart_diff],false,chart_link);
            var precise_lv = (row[chart_diff] === 'we_kanji') ? `☆${row[precise_lv_display]}` : row[precise_lv_display];
            var match = row[simple_lv].match(/^([0-9]{1,2})(\+)?$/);
            if (match) {
                var lvnum = match[1];
                var plus = (match[2] === '+');

                if (plus) {
                    return `<div class="inner-wrap"><span class="diff-name">${chart_diff_display}</span><span class="lv-num-wrap"><span class="lv-num-simple"><span class="num">${lvnum}</span><span class="plus">+</span></span><span class="lv-num-precise">${precise_lv}</span></span></div>`;
                } else {
                    return `<div class="inner-wrap"><span class="diff-name">${chart_diff_display}</span><span class="lv-num-wrap"><span class="lv-num-simple"><span class="num">${lvnum}</span></span><span class="lv-num-precise">${precise_lv}</span></span></div>`;
                }
            } else {
                return `<div class="inner-wrap"><span class="diff-name">${chart_diff_display}</span><span class="lv-num-wrap"><span class="lv-num-simple"><span class="num">${row[simple_lv]}</span></span><span class="lv-num-precise">${precise_lv}</span></span></div>`;
            }
        }
        else {
            return data;
        }
    }
}

function renderChartLinkBtn(chart_link) {
    return function ( data, type, row ) {
        if ( type === 'display' ) {
            return chartLinkBtn(row['chart_link'])
        } else {
            return data
        }
    }
}

function chartLinkBtn(chart_link) {
    if ( chart_link !== '' ) {
        return `<a class="btn chartlink" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();" href="https://sdvx.in/chunithm/${chart_link}.htm">
                    <span class="img"></span><span>譜面確認</span>
                </a><span class="chart-provider">sdvx.in 提供</span>`;
    } else {
        return '';
    }
}

function renderChartDifficultyName(chart_diff, chart_link) {
    return function ( data, type, row ) {
        if ( type === 'display' ) {
            var chart_diff_display = convertDifficultyNames(row[chart_diff],false,chart_link);       

            return '<span class="diff-name">' + chart_diff_display + '</span>';
        }
        else {
            return data;
        }
    }
}

function convertDifficultyNames(src, sort, chart_list) {
    const chart_diff_display = chart_list[src];

    if (sort) {
        var index = Object.keys(chart_list).indexOf(src) + 1;
        // For maimai
        if (src.startsWith("dx_")) {
            index -= 1;
        }
        if (index.toString().length === 1) {
            index = '0' + index;
        }
        return `${index} ${chart_diff_display}`;
    }

    return chart_diff_display;
}

function sortByDifficultyCategory(column, chart_list) {
    return function (row_a, row_b) {
        return convertDifficultyNames(row_a[column],true,chart_list).localeCompare(convertDifficultyNames(row_b[column],true,chart_list));
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

function flattenMusicData(data, flat_view, chart_list, process_chart_data) {
    if (flat_view) {
        return data
            .map(obj =>
                Object.keys(chart_list).map(chart_diff => process_chart_data(obj, chart_diff))
            )
            .flat()
            .filter(obj => !!obj);
    } else {
        return data;
    }
}

function formatDate(inputDate, dateFormat) {
    // Parse input date string
    if (inputDate.length === 8) {
        var year = inputDate.slice(0, 4);
        var month = inputDate.slice(4, 6);
        var day = inputDate.slice(6, 8);
    } else if (inputDate.length === 6) {
        var year = '20' + inputDate.slice(0, 2);
        var month = inputDate.slice(2, 4);
        var day = inputDate.slice(4, 6);
    }
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

function getColumnIndexByName(column_name) {
    return columns_params.findIndex(function(item) {
        return item.name === column_name;
    });
}

function tableInitCompleteFunctions(table) {
    // Generate Filter dropdown per columns
    generateFilterDropdowns(table);

    // filter according to URL params on initial load
    applyFilterFromURLSearchParams(table, searchParams);

    // rowgroup handling on reorder
    table.on('order.dt', function() {
        toggleDateRowGroup(table);
    });

    $('#table').addClass('loading-done');
    $('html').removeClass('table-loading');

    // recalculate columns on colvis change event
    $('#table').on( 'column-visibility.dt', function () {
        $.fn.dataTable
            .tables( { visible: true, api: true } )
            .columns.adjust();
    } );

    // Chart level selectbox
    $('select#chart_lev').on('change', function(){
        var select = $(this);
        var val = $(this).val();
        var val_e = $.fn.dataTable.util.escapeRegex(
            $(this).val()
        );

        // simply filter if select is changed on /lv/ page
        if( select.data("type") == "filter") {
            table.api().column('chart_lev:name').search(val_e ? '^' + val_e + '$' : '', true, false);

            updateQueryStringParameter('chart_lev',val);

            table.api().draw();
        } 
        // redirect to /lv/ subpage with querystring if selected on main page
        else {
            window.location.href = './lv?chart_lev=' + encodeURIComponent(val);
        }
    });

    // Reset Search
    $('button.reset-search').on('click', function(){
        table.api()
            .order(default_order) //FIXME: why doesn't work with just calling var?
            .search('')
            .columns().search('')
            .draw();

        clearQueryStringParameter();
        toggleDateRowGroup(table);

        $('.toolbar.filters select').prop('selectedIndex',0).removeClass('changed');
    });
}

function generateFilterDropdowns(table) {
    var rows = table.api().rows().data();

    table.api().columns().every(function () {
        var order = table.api().order();
        var column = this;
        var column_data = column.data();
        var column_param = columns_params[column.index()];

        if (("filterable" in column_param) && (column_param.filterable == true)) {
            var selectWrap = $('<div class="select-wrap ' + column_param.className + '"><span class="label">' + column_param.displayTitle + '</span></div>')
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
                if (column.index() === getColumnIndexByName('date') || (val_e === "" && order[0][0] === getColumnIndexByName('date'))) {
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
}

function applyFilterFromURLSearchParams(table, searchParams) {
    if ('URLSearchParams' in window) {
        // apply filters
        searchParams.forEach(function (value, key) {
            table.api().columns().every(function () {
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

        table.api().draw();
    }
}

function toggleDateRowGroup(table) {
    var order = table.api().order();
    var search = table.api().columns().search();
    var searchActive = false;

    for (let k = 0; k < search.length; k = k + 1) {
        if (k in search && search[k] !== "") {
            searchActive = true;
            break;
        }
    }

    // Disable rowgroup unless sorting by date
    if (order[0][0] !== getColumnIndexByName('date')) {
        table.api().rowGroup().disable();
        // console.log('group disabled (sorting by non-date column)');
        return;
    }
    // enable rowgroup if sorting by date AND search is inactive
    else if ((order[0][0] === getColumnIndexByName('date')) && !searchActive) {
        table.api().rowGroup().enable();
        // console.log('group enabled (sorting by date + search inactive)');
        return;
    }
    // do nothing
    else {
        // console.log('do nothing');
        return;
    }
    table.api().draw();
}