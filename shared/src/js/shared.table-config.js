var searchParams = new URLSearchParams(window.location.search);

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
            var match = row[simple_lv].match(/^([0-9]{1,2})(\+)?$/);
            if (match) {
                var lvnum = match[1];
                var plus = (match[2] === '+');

                if (plus) {
                    return `<div class="inner-wrap"><span class="lv-num-simple"><span class="num">${lvnum}</span><span class="plus">+</span></span><span class="lv-num-precise">${row[precise_lv]}</span></div>`;
                } else {
                    return `<div class="inner-wrap"><span class="lv-num-simple"><span class="num">${lvnum}</span></span><span class="lv-num-precise">${row[precise_lv]}</span></div>`;
                }
            } else {
                return `<div class="inner-wrap"><span class="lv-num-simple"><span class="num">${row[simple_lv]}</span></span><span class="lv-num-precise">${row[precise_lv]}</span></div>`;
            }
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
        return `${Object.keys(chart_list).indexOf(src) + 1} ${chart_diff_display}`;
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

$(document).ready(function() {
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