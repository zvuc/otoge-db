const ongeki_chart_list = {
  'lev_bas': 'BASIC',
  'lev_adv': 'ADVANCED',
  'lev_exc': 'EXPERT',
  'lev_mas': 'MASTER',
  'lev_lnt': 'LUNATIC'
};
const ongeki_chara_list = {
  "星咲 あかり": "ch_hoshizaki_akari",
  "藤沢 柚子": "ch_fujisawa_yuzu",
  "三角 葵": "ch_misumi_aoi",
  "高瀬 梨緒": "ch_takase_rio",
  "結城 莉玖": "ch_yuuki_riku",
  "藍原 椿": "ch_aihara_tsubaki",
  "桜井 春菜": "ch_sakurai_haruna",
  "早乙女 彩華": "ch_saotome_ayaka",
  "井之原 小星": "ch_inohara_koboshi",
  "柏木 咲姫": "ch_kashiwagi_saki",
  "九條 楓": "ch_kujo_kaede",
  "逢坂 茜": "ch_ousaka_akane",
  "珠洲島 有栖": "ch_suzushima_arisu",
  "日向 千夏": "ch_hinata_chinatsu",
  "柏木 美亜": "ch_kashiwagi_mia",
  "東雲 つむぎ": "ch_shinonome_tsumugi",
  "皇城 セツナ": "ch_sumeragi_setsuna"
};
let columns_params = [];
let default_search = [];

function setDefaultOrder() {
  if (flat_view) {
    // 難易度 , Lv , Date
    return [[getColumnIndexByName('chart_lev_i'), 'desc'],[getColumnIndexByName('chart_diff'), 'desc'],[getColumnIndexByName('date_added'), 'desc']];
  } else {
    // date , ID
    return [[getColumnIndexByName('date_added'), 'desc'],[getColumnIndexByName('id'), 'asc']];
  }
}


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
      chart_designer: obj[`${chart_diff}_designer`],
      chart_link: obj[`${chart_diff}_chart_link`]
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

function translateCharaNames() {
  return function( row, type, set, meta ) {
    if ( type === 'sort' || type === 'meta' || userLanguage === 'ja' || userTranslateCharaNamePref == "false") {
      return row.character;
    } else {
      if (row['character'] in ongeki_chara_list) {
        return getTranslation(userLanguage, ongeki_chara_list[`${row['character']}`]);
      }
      return row.character;
    }
  }
}

$(document).ready(function() {
  initTranslations().then(() => {
    columns_params = [
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
        // displayTitle: "アーティスト",
        displayTitle: getTranslation(userLanguage,'col_artist'),
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
        // displayTitle: "アーティスト",
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
        // displayTitle: "バージョン",
        displayTitle: getTranslation(userLanguage,'col_version'),
        name: "version",
        data: "version",
        className: "details version",
        filterable: true,
        render: function ( data, type, row ) {
          if ( type === 'sort' ) {
            return row.date_added;
          }
          else {
            return '<div class="inner-wrap">' + data + '<\/div>';
          }
        },
        customDropdownSortSource: "date_added",
        width: "12em"
      },
      {
        // displayTitle: "ジャンル",
        displayTitle: getTranslation(userLanguage,'col_genre'),
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
        // displayTitle: "チャプター",
        displayTitle: getTranslation(userLanguage,'col_chapter'),
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
            return `<div class="inner-wrap"><span class="chap-id-badge">${chap_id_display}</span><span class="chap-name">${row.chapter}</span></div>`;
          }
          else {
            return data;
          }
        },
        filterable: true,
        visible: false
      },
      {
        // displayTitle: "属性",
        displayTitle: getTranslation(userLanguage,'col_enemy_type'),
        name: "enemy_type",
        data: "enemy_type",
        className: "chara type",
        render: function ( data, type, row ) {
          if ( type === 'display' ) {
            return `<div class="inner-wrap"><span class="element-type-icon ${data.toLowerCase()}"><span class="icon"></span><span class="label-text">${data}</span></span></div>`;
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
        // displayTitle: "相手キャラ",
        displayTitle: getTranslation(userLanguage,'col_chara'),
        name: "character",
        data: translateCharaNames(),
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
        width: "150px",
        filterable: true
      },
      {
        // displayTitle: "相手レベル",
        displayTitle: getTranslation(userLanguage,'col_enemy_lv'),
        name: "enemy_lv",
        data: "enemy_lv",
        className: "chara enemy-lv",
        render: function ( data, type, row ) {
          if ( type === 'display' ) {
            return `<div class="inner-wrap">Lv.${data}</div>`;
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
        // displayTitle: "譜面レベル",
        displayTitle: getTranslation(userLanguage,'col_difficulty_level'),
        name: "chart_lev_i",
        data: ( flat_view ? 'chart_lev_i' : null ),
        className: "lv lv-name detail-hidden",
        render: ( flat_view ? renderChartDifficultyNameAndLv('chart_diff', 'chart_lev', 'chart_lev_i', 'chart_lev_i_display', ongeki_chart_list): null ),
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
        className: "details notecount detail-hidden",
        width: "6em",
        searchable: false,
        visible: false
      },
      {
        // displayTitle: "ベル",
        displayTitle: getTranslation(userLanguage,'col_bells'),
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
        defaultContent: "",
        width: "15em",
        className: "details detail-hidden designer",
        filterable: flat_view,
        searchable: flat_view,
      },
      {
        displayTitle: "譜面",
        name: "chart_link",
        data: ( flat_view ? "chart_link" : null ),
        defaultContent: "",
        render: ( flat_view ? renderChartLinkBtn('chart_link', 'ongeki') : null ),
        width: "5em",
        className: "details detail-hidden chart-link",
      },
      {
        // displayTitle: "追加日",
        displayTitle: getTranslation(userLanguage,'col_added_date'),
        name: "date_added",
        // data: "date_added",
        data: function( row, type, set, meta ) {
          if (row.date_updated) {
            return formatDate(row.date_updated)
          } else {
            return formatDate(row.date_added)
          }
        },
        className: "date_added detail-hidden",
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
      },
      {
        displayTitle: "NEW",
        name: "new",
        data: "new",
        searchable: false,
        visible: false
      }
    ];

    default_search = getDefaultSearchValues(columns_params);

    $.getJSON("data/music-ex.json", (data) => {
      var table = $('#table').DataTable( {
        data: flattenMusicData(data, flat_view, ongeki_chart_list, processOngekiChartData),
        "buttons": [
          {
            extend: 'colvis',
            className: 'config-btn',
            columns: '.toggle',
            text: getTranslation(userLanguage, 'colvis_btn_label'),
            collectionTitle: getTranslation(userLanguage, 'colvis_guide_text'),
            collectionLayout: "fixed",
            fade: 150
          },
          typeof namuwiki !== "undefined" ? namuwiki : ""
        ],
        "columnDefs": [
          { orderSequence: ['desc','asc'], targets: '_all'}
        ],
        "columns": columns_params,
        "searchCols": default_search,
        "createdRow": function( row, data, dataIndex, cells ) {
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
              header: renderModalHeader('オンゲキ', 'image_url', 'wikiwiki_url', 'https:\/\/wikiwiki.jp\/gameongeki\/', '譜面確認'),
              footer: renderModalFooter('オンゲキ'),
            } ),
            // renderer: $.fn.dataTable.Responsive.renderer.tableAll()
            renderer: function(api, rowIdx, columns) {
              function generateRowHtml(col, data) {
                var column_param = columns_params[col.columnIndex];
                if (!col.className.includes('detail-hidden') && !col.className.includes('lv ') && !col.className.includes('chara ')) {
                  return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                        <span class="row-label">${col.title}</span>
                        <span>${col.data}</span>
                      </div>`;
                }
              }

              function generateCharaDetailHtml(col, data) {
                if (!col.className.includes('chara ') || col.className.includes('detail-hidden')) {
                  return;
                }
                var column_param = columns_params[col.columnIndex];

                return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                      <span class="row-label">${column_param.displayTitle}</span>
                      <span>${col.data}</span>
                    </div>`;

              }

              function generatePlayableInfoHtml(col, data, prefix = '') {
                const displayDates = (region) => {
                  const dateAddedValue = data[region === 'jpn' ? 'date_added' : 'date_intl_added'];
                  const dateUpdatedValue = data[region === 'jpn' ? 'date_updated' : 'date_intl_updated'];

                  if (dateAddedValue) {
                    return `
                      <span class="line"><span class="plus-icon"></span>${getTranslation(userLanguage, 'date_added_with_date').replace('__date__', formatDate(dateAddedValue))}</span>
                      ${dateUpdatedValue ? `<span class="line"><span class="plus-icon"></span>${getTranslation(userLanguage, 'date_updated_with_date').replace('__date__', formatDate(dateUpdatedValue))}</span>` : ''}
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
                    <div class="region jp">
                      <span class="icon-wrap">
                        <svg class="symbol-32 flag-jp" aria-hidden="true" focusable="false"><use href="/shared/img/symbols.svg#flag-jp"></use></svg>
                        <span class="green-check-icon"></span>
                      </span>
                      <span class="region-label">${getTranslation(userLanguage, 'version_jp')}</span>
                      <span class="date">${displayDates('jpn')}</span>
                      ${data['key'] && data['key'] === '○' ? lock_status_html : ''}
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
                    ${(lvNumHtmlTemplate(data, chart_name))}
                  </span>
                  <span class="sub-info-wrap">
                    ${(hasPropertyAndValue(data, `${chart_name}_notes`) ?
                      `<span class="notes-detail-wrap">
                        <span class="notes"><span class="label">Notes</span><span>${data[`${chart_name}_notes`]}</span></span>
                        ${(hasPropertyAndValue(data, `${chart_name}_bells`) ? `<span class="bells"><span class="label">Bells</span><span>${data[`${chart_name}_bells`]}</span></span>` : "")}
                      </span>` : "")}
                    ${(hasPropertyAndValue(data, `${chart_name}_designer`) ? `<span class="designer"><span class="label">Designer</span><span>${data[`${chart_name}_designer`]}</span></span>` : "")}
                  </span>
                  ${(hasPropertyAndValue(data, `${chart_name}_chart_link`) ? `<span class="chart-link">${chartLinkBtn(data[`${chart_name}_chart_link`],'ongeki')}</span>` : "")}`;
              }

              function generateChartDetailHtml(col, data, chart_type) {
                if (!col.className.includes('lv ') || col.className.includes('detail-hidden')) {
                  return;
                }
                var chart_name = columns_params[col.columnIndex]['name'];

                if (chart_type === 'lunatic' && chart_name === 'lev_lnt' && hasPropertyAndValue(data, 'lev_lnt')) {
                  return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                          <span class="row-label"><span class="diff-name lv-lnt">LUNATIC</span></span>
                          <span class="content-col ${hasPropertyAndValue(data, `${chart_name}_chart_link`) && 'has-chart-link'}">
                            <span class="diff-name ${col.className}"><span>${columns_params[col.columnIndex].displayTitle}</span></span>
                            ${generateChartLevDetailHtml(data, chart_name)}</span>
                        </div>`;
                } else if (chart_type !== 'lunatic') {
                  if ((chart_name === 'lev_ult' && !hasPropertyAndValue(data, chart_name)) ||
                    (chart_name === 'lev_lnt' && !hasPropertyAndValue(data, 'lev_lnt'))) {
                    return;
                  } else {
                    return `
                      <div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                        <span class="row-label"><span class="diff-name ${col.className}">${columns_params[col.columnIndex].displayTitle}</span></span>
                        <span class="content-col ${hasPropertyAndValue(data, `${chart_name}_chart_link`) && 'has-chart-link'}">
                          <span class="diff-name ${col.className}"><span>${columns_params[col.columnIndex].displayTitle}</span></span>
                          ${generateChartLevDetailHtml(data, chart_name)}
                        </span>
                      </div>`;
                  }
                }
              }

              function generateCombinedRows(data, lunatic, columns, columns_params) {
                var normalRows = columns.map(col => generateRowHtml(col, data)).join('');
                var charaRows = columns.map(col => generateCharaDetailHtml(col, data)).join('');
                var playable_info = generatePlayableInfoHtml(columns, data);
                var chart_detail = columns.map(col => generateChartDetailHtml(col, data)).join('');
                var chart_detail_lunatic = columns.map(col => generateChartDetailHtml(col, data, 'lunatic')).join('');

                var combinedRows =
                  `<div class="table-wrapper">
                    <div class="details-table misc-details">
                      <div class="table-header"><span class="th-label">CHARACTER</span></div>
                      ${charaRows}
                      ${chara_id.substr(0,1) == "1" ? `<span class="chara-img ${enemy_type.toLowerCase()}" style="--chara-img: url('./img/chara/${chara_id}.png');"></span>`: ""}
                    </div>
                    <div class="details-table-wrap">
                      ${(lunatic ?
                      `<div class="details-table chart-details lunatic">
                        <div class="table-header"><span class="th-label">CHART</span></div>
                        ${chart_detail_lunatic}
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
              var chara_id = data['chara_id'];
              var enemy_type = data['enemy_type'];
              var lunatic = data['lunatic'] ? "lunatic" : "";

              return generateCombinedRows(data, lunatic, columns, columns_params);
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
