const colorSchemeInput = document.querySelectorAll('input[name="colorScheme"]');
const langOptionInput = document.querySelectorAll('input[name="siteLanguage"]');
const gameRegionChecks = document.querySelectorAll('input[name="gameRegion"]');
const gameRegionQuickSwitch = document.getElementById('gameRegionQuickSwitch');

// Check if the userGameRegion value is nonexistent, create one with the default value 'jp'
var currentRegion = localStorage.getItem('userGameRegion');
if (!currentRegion) {
  localStorage.setItem('userGameRegion', 'jp');
}
// Check the initial game region
const initialGameRegion = currentRegion || 'jp';
document.querySelector(`input[value="${initialGameRegion}"]`).checked = true;
gameRegionQuickSwitch.checked = (initialGameRegion === 'jp' ? false : true);
document.documentElement.setAttribute('data-game-region', currentRegion);
// switchGameRegion(); // Apply initial region

var userLanguage = localStorage.getItem('userLanguage');
if (!userLanguage) {
  localStorage.setItem('userLanguage', 'ja');
}

document.addEventListener("DOMContentLoaded", function() {
  var searchParams = new URLSearchParams(window.location.search);
  updateChartLevelSelectboxValue(searchParams);
});

function updateChartLevelSelectboxValue(searchParams) {
  // update chart_lev selectbox value on page load
  var selectedChartLevel = searchParams.get('chart_lev');
  if (selectedChartLevel !== null) {
    var value = unescapeSlashes(selectedChartLevel);
    document.querySelector('select#chart_lev').value = value;
  }
}

function unescapeSlashes(str) {
  if (str !== null) {
    // add another escaped slash if the string ends with an odd
    // number of escaped slashes which will crash JSON.parse
    let parsedStr = str.replace(/(^|[^\\])(\\\\)*\\$/, "$&\\");
    try {
      parsedStr = JSON.parse(`"${parsedStr}"`);
    } catch(e) {
      return str;
    }
    return str.replace(/(^|[^\\])(\\\\)*\\$/, "$&\\");
  } else {
    return str;
  }
}
