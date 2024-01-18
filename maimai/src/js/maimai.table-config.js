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
            ( row.buddy == "○" ? '<span class="buddy-badge">バディ<\/span>' : "") +
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
    className: "chart-type detail-hidden",
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
    //  UTAGE
    displayTitle: "UTAGE",
    name: "lev_utage",
    data: "lev_utage",
    defaultContent: "",
    className: "lv lv-utage",
    render: maimaiRenderLvNum('lev_utage'),
    customDropdownSortSource: sortByLeadingZeros('lev_utage'),
    reverseSortOrder: true,
    width: "3rem",
    filterable: flat_view ? false : true,
  },
  {
    //  UTAGE (Kanji)
    displayTitle: "UTAGE(漢字)",
    name: "lev_utage_kanji",
    data: "kanji",
    defaultContent: "",
    className: "lv lv-utage kanji",
    render: renderUtage('kanji', 'lev_utage'),
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
  // {
  //     displayTitle: "譜面作者",
  //     name: "chart_link",
  //     data: ( flat_view ? "chart_link" : null ),
  //     defaultContent: "",
  //     render: ( flat_view ? renderChartLinkBtn('chart_link') : null ),
  //     width: "5em",
  //     className: "details detail-hidden chart-link",
  // },
  {
    displayTitle: "解禁",
    name: "key",
    data: "key",
    defaultContent: "",
    className: "key detail-hidden",
    render: function ( data, type, row ) {
      if ( type === 'display' && data ) {
        return `<span class="key-icon" title="解禁必要"></span>`;
      }
      else {
        return data;
      }
    },
    searchable: false
  },
  {
    displayTitle: "追加日（Int'l Ver.）",
    name: "intl",
    data: function( row, type, set, meta ) {
      if (row.release_intl && row.release_intl !== '000000') {
        return formatDate(row.release_intl);
      }
    },
    defaultContent: "",
    className: "intl detail-hidden nowrap",
    render: function ( data, type, row ) {
      if ( type === 'display' && data) {
        return '<div class="inner-wrap">'+ data +'<\/div>';
      }
      else {
        return data;
      }
    },
    searchable: false,
    visible: false
  },
  {
    displayTitle: "追加日",
    name: "date",
    defaultContent: "",
    data: function( row, type, set, meta ) {
      return formatDate(row.date)
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
    [[getColumnIndexByName('chart_lev_i'), 'desc'],[getColumnIndexByName('chart_diff'), 'desc'],[getColumnIndexByName('date'), 'desc']] :
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

function maimaiLvNumHtmlTemplate(chart_type, cur_lev, cur_lev_i) {
  var lev_i_html = (cur_lev_i ? `<span class="lv-num-precise">${cur_lev_i}</span>` : '')

  // Find if + exists in lv number
  var match = cur_lev.match(/^([0-9]{1,2})(\+?)(\?)?$/);
  var lev_num_html = (match ? `<span class="num">${match[1]}</span>` : `<span class="num">${cur_lev}</span>`);
  var plus_html = ( match && match[2] === '+' ? '<span class="plus">+</span>' : '');
  var question_html = ( match && match[3] === '?' ? '<span class="question">?</span>' : '');

  var chart_type_html = (chart_type ? `<span class="chart-type-label">${chart_type}</span>` : '');

  return `${chart_type_html}
      <span class="lv-num-simple">${lev_num_html}${plus_html}${question_html}</span>
      ${lev_i_html}`
}

function renderUtage(kanji, lev_utage) {
  return function ( data, type, row ) {
    if ( type === 'display' ) {
      var html_output = `
        <div class="inner-wrap">
          <div class="primary">
            <span class="lv-num-simple">${row[kanji]}</span>
            <span class="lv-num-precise">${lvNumHtmlTemplate(row, lev_utage)}</span>
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
        chart_lev_i_display: `<span class="approx">${parseFloat(obj[chart_diff].replace('+', '.5')).toFixed(1)}</span>`,
        chart_notes: obj[`lev_utage_notes`],
        chart_notes_tap: obj[`lev_utage_notes_tap`],
        chart_notes_hold: obj[`lev_utage_notes_hold`],
        chart_notes_slide: obj[`lev_utage_notes_slide`],
        chart_notes_touch: obj[`lev_utage_notes_touch`],
        chart_notes_break: obj[`lev_utage_notes_break`],
        chart_designer: obj[`lev_utage_designer`],
        // chart_link: obj[`lev_utage_chart_link`]
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
        // chart_link: obj[`${chart_diff}_chart_link`]
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
      data: flattenMusicData(data, flat_view, maimai_chart_list, maimaiProcessChartData),
      "buttons": [
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
      "createdRow": function( row, data, dataIndex ) {
        if ( data.intl == "1" ) {
        $(row).addClass( 'international' );
        }
      },
      "deferRender": true,
      "dom": '<"toolbar-group"<"toolbar filters"><"toolbar search"f>><"toolbar secondary"<"info"ilB>><"table-inner"rt><"paging"p>',
      "language": localize_strings,
      "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
      "order": default_order,
      "responsive": {
        details: {
          type: 'column',
          target: 'tr',
          display: $.fn.dataTable.Responsive.display.modal( {
            header: renderModalHeader('maimai', 'image_url', 'wiki_url', 'https:\/\/gamerch.com\/maimai\/search?q=', '譜面確認用 外部出力'),
            footer: renderModalFooter('maimai'),
          } ),

          renderer: function(api, rowIdx, columns) {

            function generateRowHtml(col, data, prefix = '') {
              var column_param = columns_params[col.columnIndex];
              var column = columns_params[col.columnIndex]

              if (!col.className.includes('detail-hidden') && !col.className.includes('lv ')) {
                return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                      <span class="row-label">${column.displayTitle}</span>
                      <span>${col.data}</span>
                    </div>`;
              }
            }

            function generatePlayableInfoHtml(col, data, prefix = '') {
              if (data['release_intl']) {
                if (data['release_intl'] === '000000') {
                  var intl_date_display = '収録';
                } else {
                  var intl_date_display = `${formatDate(data['release_intl'])} 追加`;
                }
              }

              var lock_status_html = `
                <span class="lock-status">
                  <span class="key-icon"></span>
                  <span class="lock-status-text">解禁必要</span>
                <span>
              `;

              var html_output = `
              <div class="region-availability-chart">
                <div class="region jp available">
                  <span class="region-label">日本版</span>
                  <span class="date">${formatDate(data['date'])} 追加</span>
                  ${ (data['key'] && data['key'] === '○') ? lock_status_html : ''}
                </div>
                <div class="region intl ${ data['intl'] ? 'available' : 'unavailable'}">
                  <span class="region-label">International Ver.</span>
                  <span class="date">${ (data['intl'] ? intl_date_display : '未収録')}</span>
                  ${ (data['key_intl'] && data['key_intl'] === '○') ? lock_status_html : ''}
                </div>
              </div>
              `;

              return html_output;
            }

            function generateChartNoteDetailHtml(data, prefix, chart_name) {
              if (utage && data['buddy']) {
                return `
                  ${(hasPropertyAndValue(data, `${prefix}${chart_name}_left_notes`) ?
                  `<span class="notes-detail-wrap buddy">
                    <span class="side">L</span>
                    <span class="notes"><span class="label">Notes</span><span>${data[`${prefix}${chart_name}_left_notes`]}</span></span><span class="notes-sub-detail-wrap">
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_left_notes_tap`) ? `<span class="notes_tap"><span class="label">tap</span><span>${data[`${prefix}${chart_name}_left_notes_tap`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_left_notes_hold`) ? `<span class="notes_hold"><span class="label">hold</span><span>${data[`${prefix}${chart_name}_left_notes_hold`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_left_notes_slide`) ? `<span class="notes_slide"><span class="label">slide</span><span>${data[`${prefix}${chart_name}_left_notes_slide`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_left_notes_touch`) ? `<span class="notes_touch"><span class="label">touch</span><span>${data[`${prefix}${chart_name}_left_notes_touch`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_left_notes_break`) ? `<span class="notes_break"><span class="label">break</span><span>${data[`${prefix}${chart_name}_left_notes_break`]}</span></span>` : "")}
                  </span></span>`
                  : "")}
                  ${(hasPropertyAndValue(data, `${prefix}${chart_name}_right_notes`) ?
                  `<span class="notes-detail-wrap buddy">
                    <span class="side">R</span>
                    <span class="notes"><span class="label">Notes</span><span>${data[`${prefix}${chart_name}_right_notes`]}</span></span><span class="notes-sub-detail-wrap">
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_right_notes_tap`) ? `<span class="notes_tap"><span class="label">tap</span><span>${data[`${prefix}${chart_name}_right_notes_tap`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_right_notes_hold`) ? `<span class="notes_hold"><span class="label">hold</span><span>${data[`${prefix}${chart_name}_right_notes_hold`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_right_notes_slide`) ? `<span class="notes_slide"><span class="label">slide</span><span>${data[`${prefix}${chart_name}_right_notes_slide`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_right_notes_touch`) ? `<span class="notes_touch"><span class="label">touch</span><span>${data[`${prefix}${chart_name}_right_notes_touch`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_right_notes_break`) ? `<span class="notes_break"><span class="label">break</span><span>${data[`${prefix}${chart_name}_right_notes_break`]}</span></span>` : "")}
                  </span></span>`
                  : "")}
                `;
              }
              else {
                return `
                  ${(hasPropertyAndValue(data, `${prefix}${chart_name}_notes`) ?
                  `<span class="notes-detail-wrap">
                    <span class="notes"><span class="label">Notes</span><span>${data[`${prefix}${chart_name}_notes`]}</span></span><span class="notes-sub-detail-wrap">
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_notes_tap`) ? `<span class="notes_tap"><span class="label">tap</span><span>${data[`${prefix}${chart_name}_notes_tap`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_notes_hold`) ? `<span class="notes_hold"><span class="label">hold</span><span>${data[`${prefix}${chart_name}_notes_hold`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_notes_slide`) ? `<span class="notes_slide"><span class="label">slide</span><span>${data[`${prefix}${chart_name}_notes_slide`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_notes_touch`) ? `<span class="notes_touch"><span class="label">touch</span><span>${data[`${prefix}${chart_name}_notes_touch`]}</span></span>` : "")}
                    ${(hasPropertyAndValue(data, `${prefix}${chart_name}_notes_break`) ? `<span class="notes_break"><span class="label">break</span><span>${data[`${prefix}${chart_name}_notes_break`]}</span></span>` : "")}
                  </span></span>`
                  : "")}
                `;
              }
            }

            function generateChartLevDetailHtml(data, prefix, chart_name) {
              let cur_lev = data[`${prefix}${chart_name}`];
              let cur_lev_i = data[`${prefix}${chart_name}_i`] ?? '';

              var notes_detail

              return `
                <span class="main-info-wrap">
                  ${(utage ?
                    `<span class="lv-num-simple">${data['kanji']}</span>${maimaiLvNumHtmlTemplate('',`${cur_lev}`,'')}` :
                    maimaiLvNumHtmlTemplate('', `${cur_lev}`, `${cur_lev_i}`)
                  )}
                </span>
                <span class="sub-info-wrap">
                  ${generateChartNoteDetailHtml(data, prefix, chart_name)}
                  ${(hasPropertyAndValue(data, `${prefix}${chart_name}_designer`) ? `<span class="designer"><span class="label">Designer</span><span>${data[`${prefix}${chart_name}_designer`]}</span></span>` : "")}
                </span>`;
            }

            function generateChartDetailHtml(col, data, chart_type) {
              if (!col.className.includes('lv ')) {
                return;
              }

              var chart_name = columns_params[col.columnIndex]['name'];

              if (chart_type === 'std') {
                var prefix = ''
              } else if (chart_type === 'dx') {
                var prefix = 'dx_'
              } else if (chart_type === 'utage') {
                var prefix = ''
              }
              if (chart_type === 'utage' && chart_name === 'lev_utage' && hasPropertyAndValue(data, 'kanji')) {
                return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                        <span class="row-label"><span class="diff-name lv-utage">U･TA･GE${(data['buddy'] ? ' (バディ)' : '')}</span></span>
                        <span class="content-col">
                          <span class="diff-name ${col.className}"><span>U･TA･GE${(data['buddy'] ? ' (バディ)' : '')}</span></span>
                          ${generateChartLevDetailHtml(data, prefix, chart_name)}
                        </span>
                      </div>`;
              } else if (chart_type !== 'utage' && !col.className.includes('detail-hidden') && col.className.includes('lv ')) {
                if ((chart_name === 'lev_remas' && !hasPropertyAndValue(data, `${prefix}${chart_name}`)) ||
                  (chart_name === 'lev_utage_kanji') || (chart_name === 'lev_utage') ) {
                  return;
                } else {
                  return `<div class="row ${col.className}" data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                        <span class="row-label"><span class="diff-name ${col.className}">${columns_params[col.columnIndex].displayTitle}</span></span>
                        <span class="content-col">
                          <span class="diff-name ${col.className}"><span>${columns_params[col.columnIndex].displayTitle}</span></span>
                          ${generateChartLevDetailHtml(data, prefix, chart_name)}
                        </span>
                      </div>`;
                }
              }
            }

            function generateCombinedRows(data, utage, columns, columns_params) {
              let lev = `lev_bas`;
              let dx_lev = `dx_lev_bas`;

              var normalRows = columns.map(col => generateRowHtml(col, data)).join('');
              var playable_info = generatePlayableInfoHtml(columns, data);
              var chart_detail = columns.map(col => generateChartDetailHtml(col, data, 'std')).join('');
              var chart_detail_dx = columns.map(col => generateChartDetailHtml(col, data, 'dx')).join('');
              var chart_detail_utage = columns.map(col => generateChartDetailHtml(col, data, 'utage')).join('');

              var combinedRows =
                `<div class="table-wrapper">
                  <div class="details-table-wrap ${(data[dx_lev] && data[lev] ? 'dual' : '')}">
                    ${(data[dx_lev] ?
                    `<div class="details-table chart-details dx">
                      <div class="table-header"><span class="chart-type-badge dx"></span><span class="th-label">DX CHART</span></div>
                      ${(chart_detail_dx)}
                    </div>` : '')}
                    ${(data[lev] ?
                    `<div class="details-table chart-details std">
                      <div class="table-header"><span class="chart-type-badge std"></span><span class="th-label">STD CHART</span></div>
                      ${chart_detail}
                    </div>` : '')}
                    ${(utage ?
                    `<div class="details-table chart-details utage">
                      <div class="table-header"><span class="th-label">U･TA･GE CHART</span></div>
                      ${chart_detail_utage}
                    </div>` : '')}
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
            var utage = data['kanji'] ? "utage" : "";

            return generateCombinedRows(data, utage, columns, columns_params);
          }
        }
      },
      "rowGroup": {
        dataSrc: 'date',
        startRender: (!flat_view && searchParams == "" )? ( function ( rows, group ) {
          if (group === '') {
            date_display = 'NEW'
          } else {
            date_display = `${formatDate(group, 'JP')} 追加`
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
