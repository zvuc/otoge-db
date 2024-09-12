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

function lvNumHtmlTemplate(row, lev, print_lev_i=true) {
  if (row[lev]) {
    var lev = `${lev}`;
    var lev_i = `${lev}_i`;

    var lev_i_html = (print_lev_i && row[lev_i] ? `<span class="lv-num-precise">${row[lev_i]}</span>` : '')

    // Find if + exists in lv number
    var match = row[lev].match(/^([0-9]{1,2})(\+?)(\?)?$/);
    var lev_num_html = (match ? `<span class="num">${match[1]}</span>` : `<span class="num">${row[lev]}</span>`);
    var plus_html = ( match && match[2] === '+' ? '<span class="plus">+</span>' : '');
    var question_html = ( match && match[3] === '?' ? '<span class="question">?</span>' : '');

    return `<span class="lv-num-simple">${lev_num_html}${plus_html}${question_html}</span>
        ${lev_i_html}`
  }
}

function renderLvNum(lev) {
  return function ( data, type, row ) {
    if ( type === 'display' && row[lev]) {
      return `
        <div class="inner-wrap">
          ${lvNumHtmlTemplate(row, lev)}
        </div>`;
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

      if (row[chart_diff] === 'we_kanji') {
        var precise_lv = `☆${row[precise_lv_display]}`;
      } else if (row[chart_diff] === 'lev_utage') {
        var precise_lv = ``;
      } else {
        var precise_lv = row[precise_lv_display];
      }

      return `
        <div class="inner-wrap">
          <span class="diff-name">${chart_diff_display}</span>
          <span class="lv-num-wrap">
            ${lvNumHtmlTemplate(row, simple_lv, false)}
            <span class="lv-num-precise">${precise_lv}</span>
          </span>
        </div>`;
    }
    else {
      return data;
    }
  }
}

function renderChartLinkBtn(chart_link, game) {
  return function ( data, type, row ) {
    if ( type === 'display' ) {
      return chartLinkBtn(row['chart_link'], game)
    } else {
      return data
    }
  }
}

function chartLinkBtn(chart_link, game) {
  if ( chart_link && chart_link !== '' ) {
    return `<a class="btn chartlink" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();" href="https://sdvx.in/${game}/${chart_link}.htm">
          <span class="img"></span><span>${getTranslation(userLanguage, 'check_chart_guide')}</span>
        </a><span class="chart-provider">${getTranslation(userLanguage, 'chart_guide_provide_credit')}</span>`;
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
  } else {
    return '?';
  }
  var ISOdate = `${year}-${month}-${day}`

  // Format the date as "YYYY-MM-DD"
  if (dateFormat == 'weekday') {
    var days_of_week = getTranslation(userLanguage, 'days_of_week');
    var current_year = new Date().getFullYear();
    var day_of_week = days_of_week[new Date(ISOdate).getDay()];
    var year_print = (current_year == year) ? '' : `${year}/`;
    var month_print = (current_year == year && month[0] == 0) ? `${month[1]}/` : `${month}/`;
    var day_print = (current_year == year && day[0] == 0) ? `${day[1]}` : `${day}`;
    var formatted_date = `${year_print}${month_print}${day_print}(${day_of_week})`;
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
  // table.on('order.dt', function() {
  //     toggleDateRowGroup(table);
  // });

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
  $('button.reset-all').on('click', function(){
    let default_order = setDefaultOrder();

    clearFilters();
    table.api().order(default_order)
    table.api().draw();
  });

  // Reset Filters only (excluding Level filter in flat_view)
  $('button.reset-filters').on('click', function(){
    clearFilters();
    table.api().draw();
  });

  function clearFilters() {
    const currentLevelFilterVal = table.api().column('chart_lev:name').search();

    // Clear searches
    table.api().columns().search('');
    table.api().search('');

    // Restore default search presets
    const columnIndexWithDefaultSearch = columns_params.findIndex(column => column.defaultSearch !== undefined);

    if (columnIndexWithDefaultSearch !== -1) {
      if (currentRegion === 'intl') {
        table.api().column(columnIndexWithDefaultSearch).search(columns_params[columnIndexWithDefaultSearch].defaultSearch.intl, true, false)
      } else {
        table.api().column(columnIndexWithDefaultSearch).search(columns_params[columnIndexWithDefaultSearch].defaultSearch.jpn, true, false)
      }
    }

    // Restore current level filter
    if (currentLevelFilterVal) {
      table.api().column('chart_lev:name').search(currentLevelFilterVal);
    }

    // reset filter selectboxes
    $('.toolbar.filters select').prop('selectedIndex',0).removeClass('changed');

    // reset level selectbox
    if (flat_view && !currentLevelFilterVal) {
      $('select#chart_lev').prop('selectedIndex',0).removeClass('changed');
      clearQueryStringParameter();
    } else {
      clearQueryStringParameter(excludeChartLevel=true);
    }
  }


  function switchGameRegion(event) {
    if (event.target.id === 'gameRegionQuickSwitch') {
      currentRegion = event.target.checked ? 'intl' : 'jp';
    } else {
      currentRegion = document.querySelector('input[name="gameRegion"]:checked').value;
    }

    // Save the selected region in localStorage
    localStorage.setItem('userGameRegion', currentRegion);
    root.setAttribute('data-game-region', currentRegion);

    location.reload();

    // // Update default_search based on the checkbox status
    // var columnIndexWithDefaultSearch = columns_params.findIndex(column => column.defaultSearch !== undefined);

    // if (columnIndexWithDefaultSearch !== -1) {
    //   if (currentRegion === 'intl') {
    //     table.api().column(columnIndexWithDefaultSearch).search(columns_params[columnIndexWithDefaultSearch].defaultSearch.intl, true, false)
    //   } else {
    //     table.api().column(columnIndexWithDefaultSearch).search(columns_params[columnIndexWithDefaultSearch].defaultSearch.jpn, true, false)
    //   }
    // }

    // // Reset default order
    // var temp_data = table.api().data()
    // table.api().clear();
    // table.api().rows.add(temp_data);
    // table.api().order(setDefaultOrder()).draw()

    // // Toggle date columns
    // var jp_date_column = table.api().column(getColumnIndexByName('date_added'));
    // var intl_date_column = table.api().column(getColumnIndexByName('date_intl_added'));

    // if (currentRegion === 'intl') {
    //   jp_date_column.visible(false, false);
    //   intl_date_column.visible(true, false);
    // } else {
    //   jp_date_column.visible(true, false);
    //   intl_date_column.visible(false, false);
    // }

    // table.api().draw();

    // // update checkbox value
    // if (event.target.id === 'gameRegionQuickSwitch') {
    //   document.getElementById('gameRegionIntl').checked = event.target.checked;
    //   document.getElementById('gameRegionJP').checked = !event.target.checked;
    // } else {
    //   document.getElementById('gameRegionQuickSwitch').checked = (currentRegion === 'intl' ? true : false);
    // }
  }

  gameRegionChecks.forEach(input => {
    input.addEventListener('change', switchGameRegion);
  });

  gameRegionQuickSwitch.addEventListener('change', switchGameRegion);
}

function generateFilterDropdowns(table) {
  var rows = table.api().rows().data();

  table.api().columns().every(function () {
    var order = table.api().order();
    var column = this;
    var column_data = column.data();
    var column_param = columns_params[column.index()];

    if (("filterable" in column_param) && (column_param.filterable == true)) {
      var selectWrap = $(`<div class="select-wrap ${column_param.className}"></div>`)
        .appendTo($('.toolbar.filters'));
      var select = $('<select id="' + column_param.name + '"><option value="" data-default>——</option></select>')
        .appendTo(selectWrap);
      var selectLabel = $(`<span class="label">${column_param.displayTitle}</span>`)
        .appendTo(selectWrap);

      select.on('change', function () {
        var val = $(this).val();
        var val_e = $.fn.dataTable.util.escapeRegex(
          $(this).val()
        );

        appendSelectboxStateClass($(this), val);

        // var val = $(this).val();

        // when applying filter, control rowgroup visibility
        if (column.index() === getColumnIndexByName('date_added') || (val_e === "" && order[0][0] === getColumnIndexByName('date_added'))) {
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

  $(`<button class="btn reset-filters">
    <svg class="symbol icon-cross" aria-hidden="true" focusable="false"><use href="/shared/img/symbols.svg#icon-cross"></use></svg>
    ${getTranslation(userLanguage, 'clear_filters')}
    </button>`).appendTo($('.toolbar.filters'));
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

function toggleDateRowGroup(table, default_search) {
  let order = table.api().order();
  // console.log(order);
  let search = table.api().columns().search();
  let searchActive = isSearchActive(search, default_search);

  // console.log(searchActive);
  if (searchActive) {
    return;
  }

  // Disable rowgroup unless sorting by date
  if (order[0][0] !== getColumnIndexByName('date_added') || order[0][0] !== getColumnIndexByName('date_intl_added')) {
    // console.log('rowgroup disabled');
    table.api().rowGroup().disable();
  }
  // enable rowgroup if sorting by date
  if (order[0][0] === getColumnIndexByName('date_added')) {
    // console.log('rowgroup enabled');
    table.api().rowGroup().dataSrc(function(row) {
      if (row.date_updated) {
        return row.date_updated;
      } else {
        return row.date_added;
      }
    }).enable();
  }
  else if (order[0][0] === getColumnIndexByName('date_intl_added')) {
    table.api().rowGroup().dataSrc(function(row) {
      if (row.date_intl_updated) {
        return row.date_intl_updated;
      } else {
        return row.date_intl_added;
      }
    }).enable();
  }
}

function isSearchActive(search, default_search) {
  for (let k = 0; k < search.length; k = k + 1) {
    if (search[k] !== '') {
      // console.log(`search[${k}]: ${search[k]}`);

      // pass if search value matches default search
      if (search[k] === default_search[k].sSearch) {
        // console.log('current active search is default search');
        continue;
      }
      return true;
    }
  }
  return false;
}

function getDefaultSearchValues(columnsParams, isIntl = false) {
  if (isIntl) {
    return columnsParams.map(column =>
      (column.defaultSearch !== undefined) ? {"search": column.defaultSearch.intl, "regex": true, "smart": false} : null
    );
  }
  // return Array(columnsParams.length).fill(null);
  return columnsParams.map(column =>
      (column.defaultSearch !== undefined) ? {"search": column.defaultSearch.jpn, "regex": true, "smart": false} : null
    );
}

function renderModalHeader(game_name, image_col, wiki_url_col, wiki_url_base, youtube_search_term='譜面確認') {
  return function(row) {
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
    var image_url = data[image_col];
    var wiki_url_guess = `${wiki_url_base}${encoded_title}`;

    var wiki_url = data[wiki_url_col] ? data[wiki_url_col] : wiki_url_guess;

    return `
      <div class="modal-header" style="--img:url(jacket/${image_url});">
        <span class="header-img"></span>
        <span class="header-img-overlay"></span>
        <div class="img-wrap">
          <img src="jacket/${image_url}" />
        </div>
        <div class="content-wrap">
          <span class="title">${data.title}</span>
          <span class="artist">${data.artist}</span>
          <div class="quicklinks">
            <a class="wiki" href="${wiki_url}" target="_blank" rel="noopener noreferrer nofollow">Wiki</a>
            <a class="youtube" href="https://youtube.com/results?search_query=${game_name}+${youtube_search_term}+${encoded_title}" target="_blank" rel="noopener noreferrer nofollow"></a>
          </div>
        </div>
      </div>`;
  }
}

function renderModalFooter(game_name) {
  return function(row) {
    var data = row.data();
    return `
      <div class="modal-footer">
        <div class="report">
          <a class="report-btn"
            href="https://twitter.com/intent/tweet?text=@otoge_db%0A%E3%80%90%23${game_name}_DB%20%E6%83%85%E5%A0%B1%E6%8F%90%E4%BE%9B%E3%80%91%0A%E6%9B%B2%E5%90%8D%EF%BC%9A${encodeURIComponent(data.title)}%0A%E8%AD%9C%E9%9D%A2%EF%BC%9A"
            target="_blank" rel="noopener noreferrer nofollow">${getTranslation(userLanguage,'report_twitter')}</a>
        </div>
      </div>`;
  }
}
