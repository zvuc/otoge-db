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