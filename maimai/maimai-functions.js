const maimai_chart_list={lev_bas:"BASIC",dx_lev_bas:"BASIC",lev_adv:"ADVANCED",dx_lev_adv:"ADVANCED",lev_exp:"EXPERT",dx_lev_exp:"EXPERT",lev_mas:"MASTER",dx_lev_mas:"MASTER",lev_remas:"Re:MASTER",dx_lev_remas:"Re:MASTER",lev_utage:"U·TA·GE"};var columns_params=[{displayTitle:"ID (system)",name:"id",data:"sort",defaultContent:"",className:"id detail-hidden",visible:!1},{displayTitle:"#",name:"index",data:"id",defaultContent:"",className:"id detail-hidden",data:function(e){return e.id},render:renderInWrapper(),width:"20px",searchable:!1,visible:!1},{displayTitle:"アルバムアート",name:"jacket",data:"image_url",defaultContent:"",className:"jacket detail-hidden",render:function(e){return'<span class="img-wrap"><img src="jacket/'+e+'"/></span>'},width:"50px",orderable:!1,searchable:!1},{displayTitle:"曲名",name:"title",data:"title",defaultContent:"",className:"title-artist detail-hidden",render:function(e,a,t){return"display"===a?'<div class="inner-wrap"><span class="title">'+e+'</span><span class="dash hidden"> - </span><span class="artist-display hidden">'+t.artist+"</span></div>":"filter"===a?e:t.reading},width:"80vw"},{displayTitle:"曲名 (読み)",name:"reading",data:"reading",defaultContent:"",className:"reading",visible:!1,searchable:!1},{displayTitle:"アーティスト",name:"title_merged",data:"title",defaultContent:"",className:"artist detail-hidden",render:function(e,a,t){return"display"===a?'<div class="inner-wrap"><span class="artist-display hidden">'+t.artist+"</span></div>":t.reading},searchable:!1},{displayTitle:"アーティスト",name:"artist",data:"artist",defaultContent:"",className:"artist detail-hidden",visible:!1},{displayTitle:"BPM",name:"bpm",data:"bpm",defaultContent:"",className:"details bpm",searchable:!1,visible:!1},{displayTitle:"バージョン",name:"version",data:maimaiRenderVersionName(),defaultContent:"",className:"details version",filterable:!0,customDropdownSortSource:"version",width:"12em"},{displayTitle:"ジャンル",name:"category",data:"catcode",defaultContent:"",className:"details category",render:renderInWrapper(),width:"12em",filterable:!0},{displayTitle:"DX/Std",name:"chart_type",data:maimaiGetChartTypes(),defaultContent:"",className:"chart-type",render:maimaiRenderChartTypeBadges(),width:"3rem",filterable:!flat_view},{displayTitle:"BASIC",name:"lev_bas",data:maimaiProcessLvData("lev_bas","lev_bas_i"),defaultContent:"",className:"lv lv-bsc",render:maimaiRenderLvNum("lev_bas"),customDropdownSortSource:sortByLeadingZeros("lev_bas"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"ADVANCED",name:"lev_adv",data:maimaiProcessLvData("lev_adv","lev_adv_i"),defaultContent:"",className:"lv lv-adv",render:maimaiRenderLvNum("lev_adv"),customDropdownSortSource:sortByLeadingZeros("lev_adv"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"EXPERT",name:"lev_exp",data:maimaiProcessLvData("lev_exp","lev_exp_i"),defaultContent:"",className:"lv lv-exp",render:maimaiRenderLvNum("lev_exp"),customDropdownSortSource:sortByLeadingZeros("lev_exp"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"MASTER",name:"lev_mas",data:maimaiProcessLvData("lev_mas","lev_mas_i"),defaultContent:"",className:"lv lv-mas",render:maimaiRenderLvNum("lev_mas"),customDropdownSortSource:sortByLeadingZeros("lev_mas"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"Re:MASTER",name:"lev_remas",data:maimaiProcessLvData("lev_remas","lev_remas_i"),defaultContent:"",className:"lv lv-remas",render:maimaiRenderLvNum("lev_remas"),customDropdownSortSource:sortByLeadingZeros("lev_remas"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"UTAGE (Kanji)",name:"lev_utage",data:"kanji",defaultContent:"",className:"lv lv-utage kanji",render:renderUtage("kanji","lev_utage"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"UTAGE",name:"lev_utage",data:"lev_utage",defaultContent:"",className:"lv lv-utage",customDropdownSortSource:sortByLeadingZeros("lev_utage"),reverseSortOrder:!0,width:"3rem",filterable:!flat_view},{displayTitle:"譜面",name:"chart_diff",data:function(e,a,t,s){return 1==flat_view?"sort"===a||"meta"===a?e.chart_diff:convertDifficultyNames(e.chart_diff,!1,maimai_chart_list):null},defaultContent:"",className:"lv-name detail-hidden",width:"3rem",createdCell:flat_view?function(e,a,t,s,l){$(e).addClass(t.chart_diff)}:null,render:flat_view?renderChartDifficultyName("chart_diff",!1,maimai_chart_list):null,customDropdownSortSource:flat_view?sortByDifficultyCategory("chart_diff",maimai_chart_list):null,filterable:flat_view,visible:!1},{displayTitle:"難易度グループ",name:"chart_lev",data:flat_view?"chart_lev":null,defaultContent:"",className:"lv detail-hidden",width:"4rem",customDropdownSortSource:function(e){e&&sortByLeadingZeros("chart_lev")},reverseSortOrder:!0,visible:!1},{displayTitle:"譜面レベル",name:"chart_lev_i",data:flat_view?"chart_lev_i":null,defaultContent:"",className:"lv lv-name detail-hidden",render:flat_view?renderChartDifficultyNameAndLv("chart_diff","chart_lev","chart_lev_i","chart_lev_i_display",maimai_chart_list):null,width:"4rem",createdCell:flat_view?function(e,a,t,s,l){$(e).addClass(t.chart_diff)}:null,searchable:!1,visible:flat_view},{displayTitle:"ノート数",name:"chart_notes",data:flat_view?"chart_notes":null,defaultContent:"",className:"details notecount detail-hidden nowrap",width:"8em",searchable:!1},{displayTitle:"TAP",name:"chart_notes_tap",data:flat_view?"chart_notes_tap":null,defaultContent:"",className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"HOLD",name:"chart_notes_hold",data:flat_view?"chart_notes_hold":null,defaultContent:"",className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"SLIDE",name:"chart_notes_slide",data:flat_view?"chart_notes_slide":null,defaultContent:"",className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"TOUCH",name:"chart_notes_touch",data:flat_view?"chart_notes_touch":null,defaultContent:"",className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"BREAK",name:"chart_notes_break",data:flat_view?"chart_notes_break":null,defaultContent:"",className:"details notecount detail-hidden",width:"5em",searchable:!1,visible:!1},{displayTitle:"譜面作者",name:"chart_designer",data:flat_view?"chart_designer":null,defaultContent:"",width:"15em",className:"details detail-hidden designer",filterable:flat_view,searchable:flat_view},{displayTitle:"譜面作者",name:"chart_link",data:flat_view?"chart_link":null,defaultContent:"",render:flat_view?renderChartLinkBtn("chart_link"):null,width:"5em",className:"details detail-hidden chart-link"},{displayTitle:"追加日",name:"date",defaultContent:"",data:function(e,a,t,s){return formatDate(e.release)},className:"date",render:function(e,a,t){return"display"===a?'<div class="inner-wrap">'+e+"</div>":e},reverseSortOrder:!0,width:"4em",filterable:!0},{displayTitle:"NEW",name:"new",data:"newflag",defaultContent:"",className:"detail-hidden",searchable:!1}],default_order=flat_view?[[getColumnIndexByName("chart_lev"),"desc"],[getColumnIndexByName("chart_diff"),"desc"],[getColumnIndexByName("date"),"desc"]]:[[getColumnIndexByName("date"),"desc"],[getColumnIndexByName("id"),"asc"]];function maimaiGetChartTypes(){return function(e,a){let t="lev_bas",s="dx_lev_bas";return e[s]&&!e[t]?"DX":e[t]&&!e[s]?"Std":e[s]&&e[t]?"DX & Std":e.kanji?"UTAGE":void 0}}function maimaiRenderChartTypeBadges(){return function(e,a,t){if("display"===a){if(flat_view)if(t.chart_diff.startsWith("dx_"))var s=t.chart_diff;else var l=t.chart_diff;else l="lev_bas",s="dx_lev_bas";var n="",i="";if(t[s])n='<span class="chart-type-badge dx"></span>';if(t[l])i='<span class="chart-type-badge std"></span>';return`<div class="inner-wrap">${n}${i}</div>`}return e}}function maimaiProcessLvData(e,a){return function(a,t){let s="dx_"+e;return a[s]&&!a[e]?a[s]:a[e]&&!a[s]?a[e]:a[s]&&a[e]?a[s]:void 0}}function maimaiRenderLvNum(e){return function(a,t,s){if("display"===t){var l=e+"_i",n="dx_"+e,i="dx_"+l,r="",d="";if(s[n]&&!s[e]){d="DX",r=s[n];var c=s[i]}if(s[e]&&!s[n])d="Std",r=s[e],c=s[l];if(s[n]&&s[e]){d="DX",r=s[n],c=s[i];var o="Std",m=s[e],_=s[l]}return s[n]&&s[e]?`\n                    <div class="inner-wrap">\n                        <div class="primary">${maimaiLvNumHtmlTemplate(d,r,c)}</div>\n                        <div class="secondary">${maimaiLvNumHtmlTemplate(o,m,_)}</div>\n                    </div>`:s[e]&&"lev_remas"===e&&s.dx_lev_mas||s[n]&&"dx_lev_remas"===n&&s.lev_mas?`\n                    <div class="inner-wrap ${"dx_lev_remas"===e?"reverse":""}">\n                        <div class="primary empty">${maimaiLvNumHtmlTemplate("--","--","")}</div>\n                        <div class="secondary">${maimaiLvNumHtmlTemplate(d,r,c)}</div>\n                    </div>`:`\n                    <div class="inner-wrap">\n                        <div class="primary ${""===r?"empty":""}">${maimaiLvNumHtmlTemplate(d,r,c)}</div>\n                    </div>`}return a}}function maimaiLvNumHtmlTemplate(e,a,t){var s=t?`<span class="lv-num-precise">${t}</span>`:"",l=a.match(/^([0-9]{1,2})(\+)?$/);return`<span class="chart-type-label">${e}</span>\n            <span class="lv-num-simple">${l?`<span class="num">${l[1]}</span>`:a}${l&&"+"===l[2]?'<span class="plus">+</span>':""}</span>\n            ${s}`}function renderUtage(e,a){return function(t,s,l){if("display"===s){var n=`\n                <div class="inner-wrap">\n                    <div class="primary">\n                        <span class="lv-num-simple">${l[e]}</span>\n                        <span class="lv-num-precise">${l[a]}</span>\n                    </div>\n                </div>`;return l[e]?n:""}return t}}function maimaiProcessChartData(e,a){return e[a]?"kanji"===a?{...e,chart_diff:a,chart_lev:e[a],chart_lev_i:e.lev_utage,chart_lev_i_display:e.lev_utage,chart_notes:e.lev_utage_notes,chart_notes_tap:e.lev_utage_notes_tap,chart_notes_hold:e.lev_utage_notes_hold,chart_notes_slide:e.lev_utage_notes_slide,chart_notes_touch:e.lev_utage_notes_touch,chart_notes_break:e.lev_utage_notes_break,chart_designer:e.lev_utage_designer,chart_link:e.lev_utage_chart_link}:{...e,chart_diff:a,chart_lev:e[a],chart_lev_i:parseFloat(e[a+"_i"]||e[a].replace("+",".5")),chart_lev_i_display:e[a+"_i"]||`<span class="approx">${parseFloat(e[a].replace("+",".5")).toFixed(1)}</span>`,chart_notes:e[a+"_notes"],chart_notes_tap:e[a+"_notes_tap"],chart_notes_hold:e[a+"_notes_hold"],chart_notes_slide:e[a+"_notes_slide"],chart_notes_touch:e[a+"_notes_touch"],chart_notes_break:e[a+"_notes_break"],chart_designer:e[a+"_designer"],chart_link:e[a+"_chart_link"]}:null}function maimaiRenderVersionName(){return function(e,a,t,s){if("sort"===a||"meta"===a)return e.version;{const a={1e4:"maimai",11e3:"maimai PLUS",12e3:"GreeN",13e3:"GreeN PLUS",14e3:"ORANGE",15e3:"ORANGE PLUS",16e3:"PiNK",17e3:"PiNK PLUS",18e3:"MURASAKi",18500:"MURASAKi PLUS",19e3:"MiLK",19500:"MiLK PLUS",19900:"FiNALE",2e4:"でらっくす",20500:"でらっくす PLUS",21e3:"Splash",21500:"Splash PLUS",22e3:"UNiVERSE",22500:"UNiVERSE PLUS",23e3:"FESTiVAL",23500:"FESTiVAL PLUS",24e3:"BUDDiES"};let t=null;for(const s in a)e.version>=s&&(null===t||s>t)&&(t=s);return a[t]}}}$(document).ready((function(){$.getJSON("data/music-ex.json",(e=>{$("#table").DataTable({data:flattenMusicData(e,flat_view,maimai_chart_list,maimaiProcessChartData),buttons:[{extend:"colvis",className:"config-btn",columns:".toggle",text:"カラムON/OFF",collectionTitle:"表示するカラムを選択",collectionLayout:"fixed",fade:150}],columns:columns_params,deferRender:!0,dom:'<"toolbar-group"<"toolbar filters"><"toolbar search"f>><"toolbar secondary"<"info"ilB>><"table-inner"rt><"paging"p>',language:{emptyTable:"テーブルにデータがありません",info:replaceUnitText(" _TOTAL_unit (_START_〜_END_ 表示中)"),infoEmpty:replaceUnitText(" 0 unit"),infoFiltered:replaceUnitText("（全 _MAX_ unit）"),infoPostFix:"",infoThousands:",",lengthMenu:"1ページ表示 _MENU_",loadingRecords:"読み込み中...",processing:"処理中...",search:"検索",searchPlaceholder:"曲名・アーティスト",zeroRecords:"一致するレコードがありません",paginate:{sFirst:"先頭",sLast:"最終",sNext:"NEXT",sPrevious:"PREV"},aria:{sSortAscending:": 列を昇順に並べ替えるにはアクティブにする",sSortDescending:": 列を降順に並べ替えるにはアクティブにする"}},lengthMenu:[[25,50,100,-1],[25,50,100,"All"]],order:default_order,responsive:{details:{type:"column",target:"tr",display:$.fn.dataTable.Responsive.display.modal({header:function(e){var a=e.data(),t=encodeURIComponent(a.title.replaceAll("&","＆").replaceAll(":","：").replaceAll("[","［").replaceAll("]","］").replaceAll("#","＃").replaceAll('"',"”")),s="https://gamerch.com/maimai/search?q="+t,l=a.wiki_url?a.wiki_url:s;return'<div class="modal-header" style="--img:url(jacket/'+a.image_url+');"><span class="header-img"></span><span class="header-img-overlay"></span><div class="img-wrap"><img src="jacket/'+a.image_url+'"/></div><div class="content-wrap"><span class="title">'+a.title+'</span><span class="artist">'+a.artist+'</span><div class="quicklinks"><a class="wiki" href="'+l+'" target="_blank" rel="noopener noreferer nofollow">Wiki</a><a class="youtube" href="https://youtube.com/results?search_query=maimai+譜面確認+'+t+'" target="_blank" rel="noopener noreferer nofollow"></a></div></div></div>'},footer:function(e){var a=e.data();return'<div class="modal-footer"><div class="report"><a class="report-btn" href="https://twitter.com/intent/tweet?text=@zvuc_%0A%E3%80%90%23maimai_DB%20%E6%83%85%E5%A0%B1%E6%8F%90%E4%BE%9B%E3%80%91%0A%E6%9B%B2%E5%90%8D%EF%BC%9A'+encodeURIComponent(a.title)+'%0A%E8%AD%9C%E9%9D%A2%EF%BC%9A" target="_blank" rel="noopener noreferer nofollow">💬 足りない情報・間違いを報告する （Twitter）</a></div></div>'}}),renderer:function(e,a,t){function s(e,a,t=""){columns_params[e.columnIndex];if(!e.className.includes("detail-hidden")&&!e.className.includes("lv "))return`<div class="row ${e.className}" data-dt-row="${e.rowIndex}" data-dt-column="${e.columnIndex}">\n                                            <span class="row-label">${e.title}</span>\n                                            <span>${e.data}</span>\n                                        </div>`}function l(e,a,t){let s=e[`${a}${t}`],l=e[`${a}${t}_i`];return`\n                                <span class="main-info-wrap">\n                                    ${r?`<div class="inner-wrap"><span class="lv-num-simple">${e.kanji}</span><span class="lv-num-precise">${e.lev_utage}</span></div>`:maimaiLvNumHtmlTemplate("",""+s,""+l)}\n                                </span>\n                                <span class="sub-info-wrap">\n                                    ${hasPropertyAndValue(e,`${a}${t}_notes`)?`<span class="notes-detail-wrap">\n                                            <span class="notes"><span class="label">Notes</span><span>${e[`${a}${t}_notes`]}</span></span><span class="notes-sub-detail-wrap">\n                                            ${hasPropertyAndValue(e,`${a}${t}_notes_tap`)?`<span class="notes_tap"><span class="label">tap</span><span>${e[`${a}${t}_notes_tap`]}</span></span>`:""}\n                                            ${hasPropertyAndValue(e,`${a}${t}_notes_hold`)?`<span class="notes_hold"><span class="label">hold</span><span>${e[`${a}${t}_notes_hold`]}</span></span>`:""}\n                                            ${hasPropertyAndValue(e,`${a}${t}_notes_slide`)?`<span class="notes_slide"><span class="label">slide</span><span>${e[`${a}${t}_notes_slide`]}</span></span>`:""}\n                                            ${hasPropertyAndValue(e,`${a}${t}_notes_touch`)?`<span class="notes_touch"><span class="label">touch</span><span>${e[`${a}${t}_notes_touch`]}</span></span>`:""}\n                                            ${hasPropertyAndValue(e,`${a}${t}_notes_break`)?`<span class="notes_break"><span class="label">break</span><span>${e[`${a}${t}_notes_break`]}</span></span>`:""}\n                                        </span></span>`:""}\n                                    ${hasPropertyAndValue(e,`${a}${t}_designer`)?`<span class="designer"><span class="label">Designer</span><span>${e[`${a}${t}_designer`]}</span></span>`:""}\n                                </span>`}function n(e,a,t){var s=columns_params[e.columnIndex].name;if("std"===t)var n="";else if("dx"===t)n="dx_";else if("utage"===t)n="";return"utage"===t&&!e.className.includes("detail-hidden")&&e.className.includes("utage")?`<div class="row ${e.className}" data-dt-row="${e.rowIndex}" data-dt-column="${e.columnIndex}">\n                                                <span class="row-label"><span class="diff-name lv-utage">U･TA･GE</span></span>\n                                                <span class="content-col">${l(a,n,s)}</span>\n                                            </div>`:"utage"!==t&&!e.className.includes("detail-hidden")&&e.className.includes("lv ")?"lev_remas"===s&&!hasPropertyAndValue(a,`${n}${s}`)||"lev_utage"===s&&!hasPropertyAndValue(a,"lev_utage")?void 0:`<div class="row ${e.className}" data-dt-row="${e.rowIndex}" data-dt-column="${e.columnIndex}">\n                                                <span class="row-label"><span class="diff-name ${e.className}">${columns_params[e.columnIndex].displayTitle}</span></span>\n                                                <span class="content-col">\n                                                    <span class="diff-name ${e.className}"><span>${columns_params[e.columnIndex].displayTitle}</span></span>\n                                                    ${l(a,n,s)}\n                                                </span>\n                                            </div>`:void 0}var i=e.row(a).data(),r=i.kanji?"utage":"";return function(e,a,t,l){let i="lev_bas",r="dx_lev_bas";var d=t.map((e=>s(e))).join(""),c=t.map((a=>n(a,e,"std"))).join(""),o=t.map((a=>n(a,e,"dx"))).join(""),m=t.map((a=>n(a,e,"utage"))).join(""),_=`<div class="table-wrapper">\n                                    <div class="details-table-wrap ${e[r]&&e[i]?"dual":""}">\n                                        ${e[r]?`<div class="details-table chart-details dx">\n                                            <div class="table-header"><span class="chart-type-badge dx"></span><span class="th-label">DX CHART</span></div>\n                                            ${o}\n                                        </div>`:""}\n                                        ${e[i]?`<div class="details-table chart-details std">\n                                            <div class="table-header"><span class="chart-type-badge std"></span><span class="th-label">STD CHART</span></div>\n                                            ${c}\n                                        </div>`:""}\n                                        ${a?`<div class="details-table chart-details utage">\n                                            <div class="table-header"><span class="th-label">U･TA･GE CHART</span></div>\n                                            ${m}\n                                        </div>`:""}\n                                    </div>\n                                    <div class="details-table misc-details">\n                                        <div class="table-header"><span class="th-label">SONG METADATA</span></div>\n                                        ${d}\n                                    </div>\n                                </div>`;return _||!1}(i,r,t)}}},rowGroup:{dataSrc:"release",startRender:flat_view||""!=searchParams?null:function(e,a){return"<div>"+formatDate(a,"JP")+" 追加</div>"}},scrollX:!0,initComplete:function(){tableInitCompleteFunctions(this)}})}))}));
