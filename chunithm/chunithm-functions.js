const chunithm_chart_list={lev_bas:"BASIC",lev_adv:"ADVANCED",lev_exp:"EXPERT",lev_mas:"MASTER",lev_ult:"ULTIMA",we_kanji:"WORLD'S END"};var columns_params=[{displayTitle:"ID (system)",name:"id",data:"id",className:"id detail-hidden",visible:!1},{displayTitle:"#",name:"index",data:"id",className:"id detail-hidden",data:function(a){return a.id},render:renderInWrapper(),width:"20px",searchable:!1,visible:!1},{displayTitle:"アルバムアート",name:"jacket",data:"image",className:"jacket detail-hidden",render:function(a){return'<span class="img-wrap"><img src="jacket/'+a+'"/></span>'},width:"50px",orderable:!1,searchable:!1},{displayTitle:"曲名",name:"title",data:"title",className:"title-artist detail-hidden",render:function(a,e,s){return"display"===e?'<div class="inner-wrap"><span class="title">'+a+'</span><span class="dash hidden"> - </span><span class="artist-display hidden">'+s.artist+"</span></div>":"filter"===e?a:s.reading},width:"80vw"},{displayTitle:"曲名 (読み)",name:"reading",data:"reading",className:"reading",visible:!1,searchable:!1},{displayTitle:"アーティスト",name:"title_merged",data:"title",className:"artist detail-hidden",render:function(a,e,s){return"display"===e?'<div class="inner-wrap"><span class="artist-display hidden">'+s.artist+"</span></div>":s.reading},searchable:!1},{displayTitle:"アーティスト",name:"artist",data:"artist",className:"artist detail-hidden",visible:!1},{displayTitle:"BPM",name:"bpm",data:"bpm",className:"details bpm",searchable:!1,visible:!1},{displayTitle:"バージョン",name:"version",data:"version",className:"details version",filterable:!0,render:renderInWrapper(),customDropdownSortSource:"date",width:"12em"},{displayTitle:"ジャンル",name:"category",data:"catname",className:"details category",render:renderInWrapper(),width:"12em",filterable:!0},{displayTitle:"BASIC",name:"lev_bas",data:sortLevels("lev_bas"),className:"lv lv-bsc",render:renderLvNum("lev_bas"),customDropdownSortSource:sortByLeadingZeros("lev_bas"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"ADVANCED",name:"lev_adv",data:sortLevels("lev_adv"),className:"lv lv-adv",render:renderLvNum("lev_adv"),customDropdownSortSource:sortByLeadingZeros("lev_adv"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"EXPERT",name:"lev_exp",data:sortLevels("lev_exp"),className:"lv lv-exp",render:renderLvNum("lev_exp"),customDropdownSortSource:sortByLeadingZeros("lev_exp"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"MASTER",name:"lev_mas",data:sortLevels("lev_mas"),className:"lv lv-mas",render:renderLvNum("lev_mas"),customDropdownSortSource:sortByLeadingZeros("lev_mas"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"ULTIMA",name:"lev_ult",data:sortLevels("lev_ult"),className:"lv lv-ult",render:renderLvNum("lev_ult"),customDropdownSortSource:sortByLeadingZeros("lev_ult"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"WORLD'S END",name:"lev_we",data:"we_kanji",className:"lv lv-we",render:renderWorldsEnd("we_kanji","we_star"),customDropdownSortSource:sortByLeadingZeros("we_star"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"WORLD'S END☆",name:"we_star",data:convertWEStars("we_star"),className:"lv lv-we we-star",reverseSortOrder:!0,width:"3rem",searchable:!1},{displayTitle:"譜面",name:"chart_diff",data:function(a,e,s,t){return 1==flat_view?"sort"===e||"meta"===e?a.chart_diff:convertDifficultyNames(a.chart_diff,!1,chunithm_chart_list):null},className:"lv-name detail-hidden",width:"3rem",createdCell:flat_view?function(a,e,s,t,l){$(a).addClass(s.chart_diff)}:null,render:flat_view?renderChartDifficultyName("chart_diff",!1,chunithm_chart_list):null,customDropdownSortSource:flat_view?sortByDifficultyCategory("chart_diff",chunithm_chart_list):null,filterable:flat_view,visible:!1},{displayTitle:"難易度グループ",name:"chart_lev",data:flat_view?"chart_lev":null,className:"lv detail-hidden",width:"4rem",customDropdownSortSource:sortByLeadingZeros("chart_lev"),reverseSortOrder:!0,visible:!1},{displayTitle:"譜面レベル",name:"chart_lev_i",data:flat_view?"chart_lev_i":null,className:"lv lv-name detail-hidden",render:flat_view?renderChartDifficultyNameAndLv("chart_diff","chart_lev","chart_lev_i","chart_lev_i_display",chunithm_chart_list):null,width:"4rem",createdCell:flat_view?function(a,e,s,t,l){$(a).addClass(s.chart_diff)}:null,searchable:!1,visible:flat_view},{displayTitle:"ノート数",name:"chart_notes",data:flat_view?"chart_notes":null,className:"details notecount detail-hidden nowrap",width:"8em",searchable:!1},{displayTitle:"TAP",name:"chart_notes_tap",data:flat_view?"chart_notes_tap":null,className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"HOLD",name:"chart_notes_hold",data:flat_view?"chart_notes_hold":null,className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"SLIDE",name:"chart_notes_slide",data:flat_view?"chart_notes_slide":null,className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"AIR",name:"chart_notes_air",data:flat_view?"chart_notes_air":null,className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"FLICK",name:"chart_notes_flick",data:flat_view?"chart_notes_flick":null,className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"譜面作者",name:"chart_designer",data:flat_view?"chart_designer":null,defaultContent:"",width:"15em",className:"details detail-hidden designer",filterable:flat_view,searchable:flat_view},{displayTitle:"譜面",name:"chart_link",data:flat_view?"chart_link":null,defaultContent:"",render:flat_view?renderChartLinkBtn("chart_link","chunithm"):null,width:"5em",className:"details detail-hidden chart-link"},{displayTitle:"追加日",name:"date",data:function(a,e,s,t){return formatDate(a.date)},className:"date",render:function(a,e,s){return"display"===e?'<div class="inner-wrap">'+a+"</div>":a},reverseSortOrder:!0,width:"4em",filterable:!0},{displayTitle:"NEW",name:"new",data:"newflag",className:"detail-hidden",searchable:!1}],default_order=flat_view?[[getColumnIndexByName("chart_lev_i"),"desc"],[getColumnIndexByName("chart_diff"),"desc"],[getColumnIndexByName("date"),"desc"]]:[[getColumnIndexByName("date"),"desc"],[getColumnIndexByName("id"),"asc"]];function convertWEStars(a){const e={1:"1",3:"2",5:"3",7:"4",9:"5"};return e.hasOwnProperty(a)?e[a]:a}function displayWEStars(a){const e={1:"☆",3:"☆☆",5:"☆☆☆",7:"☆☆☆☆",9:"☆☆☆☆☆"};return e.hasOwnProperty(a)?e[a]:a}function renderWorldsEnd(a,e){return function(s,t,l){return"display"===t?""!==l[a]?'<div class="inner-wrap"><span class="lv-num-simple">'+l[a]+'</span><span class="lv-num-precise">☆'+convertWEStars(l[e])+"</span></div>":"":s}}function processChunithmChartData(a,e){return a[e]?"we_kanji"===e?{...a,chart_diff:e,chart_lev:a[e],chart_lev_i:convertWEStars(a.we_star),chart_lev_i_display:convertWEStars(a.we_star),chart_notes:a.lev_we_notes,chart_notes_tap:a.lev_we_notes_tap,chart_notes_hold:a.lev_we_notes_hold,chart_notes_slide:a.lev_we_notes_slide,chart_notes_air:a.lev_we_notes_air,chart_notes_flick:a.lev_we_notes_flick,chart_designer:a.lev_we_designer,chart_link:a.lev_we_chart_link}:{...a,chart_diff:e,chart_lev:a[e],chart_lev_i:parseFloat(a[e+"_i"]||a[e].replace("+",".5")),chart_lev_i_display:a[e+"_i"]||`<span class="approx">${parseFloat(a[e].replace("+",".5")).toFixed(1)}</span>`,chart_notes:a[e+"_notes"],chart_notes_tap:a[e+"_notes_tap"],chart_notes_hold:a[e+"_notes_hold"],chart_notes_slide:a[e+"_notes_slide"],chart_notes_air:a[e+"_notes_air"],chart_notes_flick:a[e+"_notes_flick"],chart_designer:a[e+"_designer"],chart_link:a[e+"_chart_link"]}:null}$(document).ready((function(){$.getJSON("data/music-ex.json",(a=>{$("#table").DataTable({data:flattenMusicData(a,flat_view,chunithm_chart_list,processChunithmChartData),buttons:[{extend:"colvis",className:"config-btn",columns:".toggle",text:"カラムON/OFF",collectionTitle:"表示するカラムを選択",collectionLayout:"fixed",fade:150}],columns:columns_params,deferRender:!0,dom:'<"toolbar-group"<"toolbar filters"><"toolbar search"f>><"toolbar secondary"<"info"ilB>><"table-inner"rt><"paging"p>',language:localize_strings,lengthMenu:[[25,50,100,-1],[25,50,100,"All"]],order:default_order,responsive:{details:{type:"column",target:"tr",display:$.fn.dataTable.Responsive.display.modal({header:renderModalHeader("CHUNITHM","image","wikiwiki_url","https://wikiwiki.jp/chunithmwiki/","譜面確認"),footer:renderModalFooter("CHUNITHM")}),renderer:function(a,e,s){function t(a,e){columns_params[a.columnIndex];if(!a.className.includes("detail-hidden")&&!a.className.includes("lv "))return`<div class="row ${a.className}" data-dt-row="${a.rowIndex}" data-dt-column="${a.columnIndex}">\n                                            <span class="row-label">${a.title}</span>\n                                            <span>${a.data}</span>\n                                        </div>`}function l(a,e){a[""+e],a[e+"_i"];return`\n                                <span class="main-info-wrap">\n                                    ${i?`<div class="inner-wrap"><span class="lv-num-simple">${a.we_kanji}</span><span class="lv-num-precise">${displayWEStars(a.we_star)}</span></div>`:lvNumHtmlTemplate(a,e)}\n                                </span>\n                                <span class="sub-info-wrap">\n                                    ${hasPropertyAndValue(a,e+"_notes")?`<span class="notes-detail-wrap">\n                                            <span class="notes"><span class="label">Notes</span><span>${a[e+"_notes"]}</span></span><span class="notes-sub-detail-wrap">\n                                            ${hasPropertyAndValue(a,e+"_notes_tap")?`<span class="notes_tap"><span class="label">tap</span><span>${a[e+"_notes_tap"]}</span></span>`:""}\n                                            ${hasPropertyAndValue(a,e+"_notes_hold")?`<span class="notes_hold"><span class="label">hold</span><span>${a[e+"_notes_hold"]}</span></span>`:""}\n                                            ${hasPropertyAndValue(a,e+"_notes_slide")?`<span class="notes_slide"><span class="label">slide</span><span>${a[e+"_notes_slide"]}</span></span>`:""}\n                                            ${hasPropertyAndValue(a,e+"_notes_air")?`<span class="notes_air"><span class="label">air</span><span>${a[e+"_notes_air"]}</span></span>`:""}\n                                            ${hasPropertyAndValue(a,e+"_notes_flick")?`<span class="notes_flick"><span class="label">flick</span><span>${a[e+"_notes_flick"]}</span></span>`:""}\n                                        </span></span>`:""}\n                                    ${hasPropertyAndValue(a,e+"_designer")?`<span class="designer"><span class="label">Designer</span><span>${a[e+"_designer"]}</span></span>`:""}\n                                </span>\n                                ${hasPropertyAndValue(a,e+"_chart_link")?`<span class="chart-link">${chartLinkBtn(a[e+"_chart_link"],"chunithm")}</span>`:""}`}function n(a,e,s){if(a.className.includes("lv ")&&!a.className.includes("detail-hidden")){var t=columns_params[a.columnIndex].name;return"worldsend"===s&&"lev_we"===t&&hasPropertyAndValue(e,"we_kanji")?`<div class="row ${a.className}" data-dt-row="${a.rowIndex}" data-dt-column="${a.columnIndex}">\n                                                <span class="row-label"><span class="diff-name lv-we">WORLD'S END</span></span>\n                                                <span class="content-col ${hasPropertyAndValue(e,t+"_chart_link")&&"has-chart-link"}">\n                                                    <span class="diff-name ${a.className}"><span>${columns_params[a.columnIndex].displayTitle}</span></span>\n                                                    ${l(e,t)}\n                                                </span>\n                                            </div>`:"worldsend"!==s?"lev_ult"===t&&!hasPropertyAndValue(e,t)||"lev_we"===t||"we_star"===t?void 0:`<div class="row ${a.className}" data-dt-row="${a.rowIndex}" data-dt-column="${a.columnIndex}">\n                                                <span class="row-label"><span class="diff-name ${a.className}">${columns_params[a.columnIndex].displayTitle}</span></span>\n                                                <span class="content-col ${hasPropertyAndValue(e,t+"_chart_link")&&"has-chart-link"}">\n                                                    <span class="diff-name ${a.className}"><span>${columns_params[a.columnIndex].displayTitle}</span></span>\n                                                    ${l(e,t)}\n                                                </span>\n                                            </div>`:void 0}}var r=a.row(e).data(),i=r.we_kanji?"worldsend":"";return function(a,e,s,l){var r=s.map((a=>t(a))).join(""),i=s.map((e=>n(e,a))).join(""),d=s.map((e=>n(e,a,"worldsend"))).join(""),c=`<div class="table-wrapper">\n                                    <div class="details-table-wrap">\n                                        ${e?`<div class="details-table chart-details worldsend">\n                                            <div class="table-header"><span class="th-label">CHART</span></div>\n                                            ${d}\n                                        </div>`:`<div class="details-table chart-details std">\n                                            <div class="table-header"><span class="chart-type-badge std"></span><span class="th-label">CHART</span></div>\n                                            ${i}\n                                        </div>`}\n                                    </div>\n                                    <div class="details-table misc-details">\n                                        <div class="table-header"><span class="th-label">SONG METADATA</span></div>\n                                        ${r}\n                                    </div>\n                                </div>`;return c||!1}(r,i,s)}}},rowGroup:{dataSrc:"date",startRender:flat_view||""!=searchParams?null:function(a,e){return"<div>"+formatDate(e,"JP")+" 追加</div>"}},scrollX:!0,initComplete:function(){tableInitCompleteFunctions(this)}})}))}));
