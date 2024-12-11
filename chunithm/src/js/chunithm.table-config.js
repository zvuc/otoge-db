const chunithm_chart_list = {
  'lev_bas': 'BASIC',
  'lev_adv': 'ADVANCED',
  'lev_exp': 'EXPERT',
  'lev_mas': 'MASTER',
  'lev_ult': 'ULTIMA',
  'we_kanji': 'WORLD\'S END'
};
let columns_params = [];
let default_search = [];

function setDefaultOrder() {
  var regional_date_column_index = (currentRegion === 'intl' ? getColumnIndexByName('date_intl_added') : getColumnIndexByName('date_added'))

  if (flat_view) {
    // 難易度 , Lv , Date
    return [[getColumnIndexByName('chart_lev_i'), 'desc'],[getColumnIndexByName('chart_diff'), 'desc'],[regional_date_column_index, 'desc']];
  } else {
    // date , ID
    return [[regional_date_column_index, 'desc'],[getColumnIndexByName('version'), 'desc'],[getColumnIndexByName('id'), 'asc']];
  }
}

function convertWEStars(we_star) {
  const conversionTable = {
    "1": "1",
    "3": "2",
    "5": "3",
    "7": "4",
    "9": "5"
  };

  if (conversionTable.hasOwnProperty(we_star)) {
    return conversionTable[we_star];
  } else {
    return we_star;
  }
}

function displayWEStars(we_star) {
  const conversionTable = {
    "1": "☆",
    "3": "☆☆",
    "5": "☆☆☆",
    "7": "☆☆☆☆",
    "9": "☆☆☆☆☆"
  };

  if (conversionTable.hasOwnProperty(we_star)) {
    return conversionTable[we_star];
  } else {
    return we_star;
  }
}

function renderWorldsEnd(we_kanji, we_star) {
  return function ( data, type, row ) {
    if ( type === 'display' ) {
      return row[we_kanji] !== '' ? '<div class="inner-wrap"><span class="lv-num-simple"><span>' + row[we_kanji] + '<\/span><\/span><span class="lv-num-precise">☆' + convertWEStars(row[we_star]) + '<\/span><\/div>' : '';
    }
    else {
      return data;
    }
  }
}

function processChunithmChartData(obj, chart_diff) {
  if (obj[chart_diff]) {
    if (chart_diff === 'we_kanji') {
      return {
        ...obj,
        chart_diff,
        chart_lev: obj[chart_diff],
        chart_lev_i: convertWEStars(obj[`we_star`]),
        chart_lev_i_display: convertWEStars(obj[`we_star`]),
        chart_notes: obj[`lev_we_notes`],
        chart_notes_tap: obj[`lev_we_notes_tap`],
        chart_notes_hold: obj[`lev_we_notes_hold`],
        chart_notes_slide: obj[`lev_we_notes_slide`],
        chart_notes_air: obj[`lev_we_notes_air`],
        chart_notes_flick: obj[`lev_we_notes_flick`],
        chart_designer: obj[`lev_we_designer`],
        chart_link: obj[`lev_we_chart_link`]
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
        chart_notes_air: obj[`${chart_diff}_notes_air`],
        chart_notes_flick: obj[`${chart_diff}_notes_flick`],
        chart_designer: obj[`${chart_diff}_designer`],
        chart_link: obj[`${chart_diff}_chart_link`]
      };
    }
  }
  return null;
}

$(document).ready(function() {
  initTranslations().then(() => {
    columns_params = [
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
        data: "image",
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
            return `
              <div class="inner-wrap">
                <span class="title">${data}</span>
                <span class="dash hidden"> - </span>
                <span class="artist-display hidden">${row.artist}</span>
              </div>`;
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
        className: "reading",
        visible: false,
        searchable: false
      },
      {
        // Artist column (only on mobile - acts as title column on header)
        displayTitle: getTranslation(userLanguage,'col_artist'),
        name: "title_merged",
        data: "title",
        className: "artist detail-hidden",
        render: function ( data, type, row ) {
          // If display or filter data is requested, return title
          if ( type === 'display' ) {
            return `<div class="inner-wrap"><span class="artist-display hidden">${row.artist}</span></div>`;
          }
          else {
            return row.reading;
          }
        },
        searchable: false
      },
      {
        // hidden real artist column (for search)
        // アーティスト
        displayTitle: getTranslation(userLanguage,'col_artist'),
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
        // バージョン
        displayTitle: getTranslation(userLanguage,'col_version'),
        name: "version",
        data: "version",
        className: "details version",
        filterable: true,
        render: function ( data, type, row ) {
          if ( type === 'sort' ) {
            return (row.date_added || row.date_intl_added);
          }
          // use chara_id for sort
          else {
            return '<div class="inner-wrap">' + data + '<\/div>';
          }
        },
        customDropdownSortSource: "date_added",
        width: "12em",
      },
      {
        // displayTitle: "ジャンル",
        displayTitle: getTranslation(userLanguage,'col_genre'),
        name: "category",
        data: "catname",
        className: "details category",
        render: renderInWrapper(),
        width: "12em",
        filterable: true,
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
        filterable: flat_view ? false : true,
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
        name: "lev_exp",
        data: sortLevels('lev_exp'),
        className: "lv lv-exp",
        render: renderLvNum('lev_exp'),
        customDropdownSortSource: sortByLeadingZeros('lev_exp'),
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
        //  ULTIMA
        displayTitle: "ULTIMA",
        name: "lev_ult",
        data: sortLevels('lev_ult'),
        className: "lv lv-ult",
        render: renderLvNum('lev_ult'),
        customDropdownSortSource: sortByLeadingZeros('lev_ult'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
      },
      {
        //  WORLD'S END (Kanji)
        displayTitle: "WORLD'S END",
        name: "lev_we",
        data: "we_kanji",
        className: "lv lv-we",
        render: renderWorldsEnd('we_kanji', 'we_star'),
        customDropdownSortSource: sortByLeadingZeros('we_star'),
        reverseSortOrder: true,
        width: "3rem",
        filterable: flat_view ? false : true,
      },
      {
        //  WORLD'S END
        displayTitle: "WORLD'S END☆",
        name: "we_star",
        data: convertWEStars('we_star'),
        className: "lv lv-we we-star",
        reverseSortOrder: true,
        width: "3rem",
        searchable: false,
        visible: false
      },
      {
        //  chart_diff
        // displayTitle: "譜面",
        displayTitle: getTranslation(userLanguage,'col_chart'),
        name: "chart_diff",
        data:
          function( row, type, set, meta ) {
            if ( flat_view == true ) {
              if ( type === 'sort' || type === 'meta') {
                return row.chart_diff;
              }
              else {
                return convertDifficultyNames(row.chart_diff, false, chunithm_chart_list);
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
        render: flat_view ? renderChartDifficultyName('chart_diff',false,chunithm_chart_list) : null,
        customDropdownSortSource: flat_view ? sortByDifficultyCategory('chart_diff', chunithm_chart_list) : null,
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
        // displayTitle: "譜面レベル",
        displayTitle: getTranslation(userLanguage,'col_difficulty_level'),
        name: "chart_lev_i",
        data: ( flat_view ? 'chart_lev_i' : null ),
        className: "lv lv-name detail-hidden",
        render: ( flat_view ? renderChartDifficultyNameAndLv('chart_diff', 'chart_lev', 'chart_lev_i', 'chart_lev_i_display', chunithm_chart_list) : null),
        width: "4rem",
        createdCell: flat_view ? ( function( td, cellData, rowData, row, col ) {
          $(td).addClass( rowData.chart_diff );
        }) : null,
        searchable: false,
        visible: flat_view
      },
      {
        // displayTitle: "ノート数",
        displayTitle: getTranslation(userLanguage,'col_notes'),
        name: "chart_notes",
        data: ( flat_view ? "chart_notes" : null ),
        className: "details notecount detail-hidden nowrap",
        width: "8em",
        searchable: false,
        visible: false
      },
      {
        displayTitle: "TAP",
        name: "chart_notes_tap",
        data: ( flat_view ? "chart_notes_tap" : null ),
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
      },
      {
        displayTitle: "HOLD",
        name: "chart_notes_hold",
        data: ( flat_view ? "chart_notes_hold" : null ),
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
      },
      {
        displayTitle: "SLIDE",
        name: "chart_notes_slide",
        data: ( flat_view ? "chart_notes_slide" : null ),
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
      },
      {
        displayTitle: "AIR",
        name: "chart_notes_air",
        data: ( flat_view ? "chart_notes_air" : null ),
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
      },
      {
        displayTitle: "FLICK",
        name: "chart_notes_flick",
        data: ( flat_view ? "chart_notes_flick" : null ),
        className: "details notecount detail-hidden",
        width: "5em",
        searchable: false,
        visible: false
      },
      {
        // displayTitle: "譜面作者",
        displayTitle: getTranslation(userLanguage,'col_designer'),
        name: "chart_designer",
        data: ( flat_view ? "chart_designer" : null ),
        defaultContent: "",
        width: "15em",
        className: "details detail-hidden designer",
        filterable: flat_view,
        searchable: flat_view
      },
      {
        // displayTitle: "譜面",
        displayTitle: getTranslation(userLanguage,'col_chart'),
        name: "chart_link",
        data: ( flat_view ? "chart_link" : null ),
        defaultContent: "",
        render: ( flat_view ? renderChartLinkBtn('chart_link', 'chunithm') : null ),
        width: "5em",
        className: "details detail-hidden chart-link",
      },
      {
        displayTitle: "Int'l",
        name: "intl",
        data: "intl",
        defaultContent: "",
        className: "detail-hidden",
        width: "4em",
        visible: false,
        defaultSearch: {
          intl: "^(1|2)",
          jpn: "^(0|1)"
        }
      },
      {
        // displayTitle: "追加日（Int'l Ver.）",
        displayTitle: getTranslation(userLanguage,'col_added_date_intl'),
        name: "date_intl_added",
        data: function( row, type, set, meta ) {
          if (row.date_intl_updated && row.date_intl_updated !== '') {
            return formatDate(row.date_intl_updated);
          } else if (row.date_intl_added && row.date_intl_added !== '') {
            return formatDate(row.date_intl_added);
          }
        },
        defaultContent: "",
        className: "intl date detail-hidden nowrap",
        render: function ( data, type, row ) {
          if ( type === 'display' && data) {
            return '<div class="inner-wrap">'+ data +'<\/div>';
          }
          else {
            return data;
          }
        },
        reverseSortOrder: true,
        filterable: true,
        visible: (currentRegion === 'intl' ? true : false)
      },
      {
        // displayTitle: "追加日",
        displayTitle: getTranslation(userLanguage,'col_added_date'),
        name: "date_added",
        // data: "date",
        data: function( row, type, set, meta ) {
          if (row.date_updated) {
            return formatDate(row.date_updated)
          } else {
            return formatDate(row.date_added)
          }
        },
        className: "date detail-hidden",
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
        filterable: true,
        visible: (currentRegion === 'intl' ? false : true)
      },
      {
        displayTitle: "NEW",
        name: "new",
        data: "newflag",
        className: "detail-hidden", // this column is required to ensure modal displays
        searchable: false
      }
    ];

    default_search = getDefaultSearchValues(columns_params, (currentRegion === 'intl' ? true : false));

    $.getJSON((currentRegion === 'intl' ? "data/music-ex-intl.json" : "data/music-ex.json"), (data) => {
      var table = $('#table').DataTable( {
        // "ajax": {
        //     url: "data/music-ex.json",
        //     dataSrc: ""
        // },
        data: flattenMusicData(data, flat_view, chunithm_chart_list, processChunithmChartData),
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
            text: getTranslation(userLanguage, 'colvis_btn_label'),
            collectionTitle: getTranslation(userLanguage, 'colvis_guide_text'),
            collectionLayout: "fixed",
            fade: 150
          },
        ],
        "columns": columns_params,
        "searchCols": default_search,
        "createdRow": function( row, data, dataIndex, cells ) {
          if ( data.intl == "1" ) {
            $(row).addClass( 'international' );
          }
          $(cells).wrapInner('<div class="td-inner"/>');
        },
        "rowCallback": function ( row, data, displayNum ) {
          $(row)
            .css('--row-index',`${displayNum}`)
            .addClass('anim-enter')
            .on('animationend webkitAnimationEnd oAnimationEnd', function (e) {
              e.stopPropagation();
              $(row).removeClass('anim-enter')
            });

        },
        "drawCallback": function(settings) {
          toggleDateRowGroup(this, default_search);
        },
        "deferRender": true,
        "dom": '<"toolbar-group"<"toolbar filters"><"toolbar search"f>><"toolbar secondary"<"info"ilB>><"table-inner"rt><"paging"p>',
        "language": replaceUnitText(getTranslation(userLanguage, 'datatable_ui')),
        "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
        "order": setDefaultOrder(),
        "responsive": {
          details: {
            type: 'column',
            target: 'tr',
            display: $.fn.dataTable.Responsive.display.modal( {
              header: renderModalHeader('CHUNITHM', 'image', 'wikiwiki_url', 'https:\/\/wikiwiki.jp\/chunithmwiki\/', '譜面確認'),
              footer: renderModalFooter('CHUNITHM'),
            } ),
            // renderer: $.fn.dataTable.Responsive.renderer.tableAll()
            renderer: function(api, rowIdx, columns) {
              function generateRowHtml(col, data) {
                var column_param = columns_params[col.columnIndex];
                if (!col.className.includes('detail-hidden') && !col.className.includes('lv ')) {
                  return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                        <span class="row-label">${col.title}</span>
                        <span>${col.data}</span>
                      </div>`;
                }
              }

              function generatePlayableInfoHtml(col, data, prefix = '') {
                const displayDates = (region) => {
                  const dateAddedValue = data[region === 'jpn' ? 'date_added' : 'date_intl_added'];
                  const dateUpdatedValue = data[region === 'jpn' ? 'date_updated' : 'date_intl_updated'];
                  let dateUpdatedLabelTextKey = 'date_updated_with_date';

                  if (data['we_kanji'] != '') {
                    dateUpdatedLabelTextKey = 'date_updated_revived_with_date'
                  } else if (data['lev_ult'] != '') {
                    dateUpdatedLabelTextKey = 'date_updated_new_chart_with_date'
                  }

                  if (dateAddedValue) {
                    return `
                      <span class="line"><span class="plus-icon"></span>${getTranslation(userLanguage, 'date_added_with_date').replace('__date__', formatDate(dateAddedValue))}</span>
                      ${dateUpdatedValue ? `<span class="line"><span class="plus-icon"></span>${getTranslation(userLanguage, dateUpdatedLabelTextKey).replace('__date__', formatDate(dateUpdatedValue))}</span>` : ''}
                    `;
                  } else {
                    return `
                      <span class="line"><span class="green-check-icon"></span>${getTranslation(userLanguage, 'song_playable')}</span>
                    `;
                  }
                };

                const displayUnavailable = () => {
                  return `
                      <span class="line"><span class="cross-icon"></span>${getTranslation(userLanguage, 'song_unavailable')}</span>
                    `;
                };

                const lock_status_html = `
                  <span class="lock-status">
                    <span class="key-icon"></span>
                    <span class="lock-status-text">${getTranslation(userLanguage, 'unlock_needed')}</span>
                  <span>
                `;

                const html_output = `
                  <div class="region-availability-chart">
                    <div class="region jp ${data['intl'] !== "2" ? 'available' : 'unavailable'}">
                      <span class="icon-wrap">
                        <svg class="symbol-32 flag-jp" aria-hidden="true" focusable="false"><use href="/shared/img/symbols.svg#flag-jp"></use></svg>
                        <span class="green-check-icon"></span>
                      </span>
                      <span class="region-label">${getTranslation(userLanguage, 'version_jp')}</span>
                      <span class="date">${data['intl'] !== "2" ? displayDates('jpn') : displayUnavailable()}</span>
                      ${data['key'] && data['key'] === '○' ? lock_status_html : ''}
                    </div>
                    <div class="region intl ${data['intl'] !== "0" ? 'available' : 'unavailable'}">
                      <span class="icon-wrap">
                        <svg class="symbol-32 globe-asia" aria-hidden="true" focusable="false"><use href="/shared/img/symbols.svg#globe-asia"></use></svg>
                        <span class="green-check-icon"></span>
                      </span>
                      <span class="region-label">${getTranslation(userLanguage, 'version_intl')}</span>
                      <span class="date">${data['intl'] !== "0" ? displayDates('intl') : displayUnavailable()}</span>
                      ${data['key_intl'] && data['key_intl'] === '○' ? lock_status_html : ''}
                    </div>
                  </div>
                `;

                return html_output;
              }

              function generateChartLevDetailHtml(data, chart_name) {
                let cur_lev = data[`${chart_name}`];
                let cur_lev_i = data[`${chart_name}_i`];

                return `
                  <span class="main-info-wrap">
                    ${(worldsend ?
                      `<div class="inner-wrap"><span class="lv-num-simple">${data['we_kanji']}</span><span class="lv-num-precise">${displayWEStars(data['we_star'])}</span></div>` :
                      lvNumHtmlTemplate(data, chart_name)
                    )}
                  </span>
                  <span class="sub-info-wrap">
                    ${(hasPropertyAndValue(data, `${chart_name}_notes`) ?
                      `<span class="notes-detail-wrap">
                        <span class="notes"><span class="label">Notes</span><span>${data[`${chart_name}_notes`]}</span></span><span class="notes-sub-detail-wrap">
                        ${(hasPropertyAndValue(data, `${chart_name}_notes_tap`) ? `<span class="notes_tap"><span class="label">tap</span><span>${data[`${chart_name}_notes_tap`]}</span></span>` : "")}
                        ${(hasPropertyAndValue(data, `${chart_name}_notes_hold`) ? `<span class="notes_hold"><span class="label">hold</span><span>${data[`${chart_name}_notes_hold`]}</span></span>` : "")}
                        ${(hasPropertyAndValue(data, `${chart_name}_notes_slide`) ? `<span class="notes_slide"><span class="label">slide</span><span>${data[`${chart_name}_notes_slide`]}</span></span>` : "")}
                        ${(hasPropertyAndValue(data, `${chart_name}_notes_air`) ? `<span class="notes_air"><span class="label">air</span><span>${data[`${chart_name}_notes_air`]}</span></span>` : "")}
                        ${(hasPropertyAndValue(data, `${chart_name}_notes_flick`) ? `<span class="notes_flick"><span class="label">flick</span><span>${data[`${chart_name}_notes_flick`]}</span></span>` : "")}
                      </span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${chart_name}_designer`) ? `<span class="designer"><span class="label">Designer</span><span>${data[`${chart_name}_designer`]}</span></span>` : "")}
                  </span>
                  ${(hasPropertyAndValue(data, `${chart_name}_chart_link`) ? `<span class="chart-link">${chartLinkBtn(data[`${chart_name}_chart_link`], 'chunithm')}</span>` : "")}`;
              }

              function generateChartDetailHtml(col, data, chart_type) {
                if (!col.className.includes('lv ') || col.className.includes('detail-hidden')) {
                  return;
                }
                var chart_name = columns_params[col.columnIndex]['name'];

                if (chart_type === 'worldsend' && chart_name === 'lev_we' && hasPropertyAndValue(data, 'we_kanji')) {
                  return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                          <span class="row-label"><span class="diff-name lv-we">WORLD'S END</span></span>
                          <span class="content-col ${hasPropertyAndValue(data, `${chart_name}_chart_link`) && 'has-chart-link'}">
                            <span class="diff-name ${col.className}"><span>${columns_params[col.columnIndex].displayTitle}</span></span>
                            ${generateChartLevDetailHtml(data, chart_name)}
                          </span>
                        </div>`;
                } else if (chart_type !== 'worldsend') {
                  if ((chart_name === 'lev_ult' && !hasPropertyAndValue(data, chart_name)) ||
                    (chart_name === 'lev_we') || (chart_name === 'we_star')) {
                    return;
                  } else {
                    return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                          <span class="row-label"><span class="diff-name ${col.className}">${columns_params[col.columnIndex].displayTitle}</span></span>
                          <span class="content-col ${hasPropertyAndValue(data, `${chart_name}_chart_link`) && 'has-chart-link'}">
                            <span class="diff-name ${col.className}"><span>${columns_params[col.columnIndex].displayTitle}</span></span>
                            ${generateChartLevDetailHtml(data, chart_name)}
                          </span>
                        </div>`;
                  }
                }
              }

              function generateCombinedRows(data, worldsend, columns, columns_params) {
                var normalRows = columns.map(col => generateRowHtml(col, data)).join('');
                var playable_info = generatePlayableInfoHtml(columns, data);
                var chart_detail = columns.map(col => generateChartDetailHtml(col, data)).join('');
                var chart_detail_worldsend = columns.map(col => generateChartDetailHtml(col, data, 'worldsend')).join('');

                var combinedRows =
                  `<div class="table-wrapper">
                    <div class="details-table-wrap">
                      ${(worldsend ?
                      `<div class="details-table chart-details worldsend">
                        <div class="table-header"><span class="th-label">CHART</span></div>
                        ${chart_detail_worldsend}
                      </div>` :
                      `<div class="details-table chart-details std">
                        <div class="table-header"><span class="chart-type-badge std"></span><span class="th-label">CHART</span></div>
                        ${chart_detail}
                      </div>`
                      )}
                    </div>
                    <div class="details-table misc-details">
                      <div class="table-header"><span class="th-label">SONG METADATA</span></div>
                      ${normalRows}
                    </div>
                    <div class="details-table playable-info">
                      ${playable_info}
                    </div>
                  </div>`;

                return combinedRows ? combinedRows : false;
              }

              var row = api.row(rowIdx);
              var data = row.data();
              var worldsend = data['we_kanji'] ? "worldsend" : "";

              return generateCombinedRows(data, worldsend, columns, columns_params);
            }
          }
        },
        "rowGroup": {
          dataSrc: function(row) {
            if (row.date_updated) {
              return row.date_updated;
            } else {
              return row.date_added;
            }
          },
          startRender: (!flat_view && searchParams == "" )? ( function ( rows, group ) {
            if (group === '') {
              date_display = 'NEW'
            } else if (group === 'No group') {
              date_display = getTranslation(userLanguage,'date_updated_with_date').replace('__date__', '???')
            } else {
              date_display = getTranslation(userLanguage,'date_updated_with_date').replace('__date__', formatDate(group, 'weekday'))
            }
            return `<div>${date_display}</div>`;
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
});
