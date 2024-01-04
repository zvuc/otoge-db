// theme switcher
const root = document.documentElement;
const toggleSwitch = document.getElementById('themeToggleCheckbox');

if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    toggleSwitch.checked = false;
    root.setAttribute('data-theme', 'dark');
}

if (window.matchMedia('(prefers-color-scheme: light)').matches) {
    toggleSwitch.checked = true;
    root.setAttribute('data-theme', 'light');
}

// Determine appropriate transitionEvent for current browser
const getTransitionEvent = () => {
    const el = document.createElement("fakeelement");

    const transitions = {
        "transition"      : "transitionend",
        "OTransition"     : "oTransitionEnd",
        "MozTransition"   : "transitionend",
        "WebkitTransition": "webkitTransitionEnd"
    };

    for (const property in transitions){
        if (el.style[property] !== undefined){
            return transitions[property];
        }
    }
};

const transitionEvent = getTransitionEvent();


function switchTheme(e) {
    root.classList.toggle('transitioning');

    if (e.target.checked) {
        root.setAttribute('data-theme', 'light');
    }
    else {
        root.setAttribute('data-theme', 'dark');
    } 

    root.addEventListener(transitionEvent, transitionEndCallback);
}

toggleSwitch.addEventListener('change', switchTheme, false);

transitionEndCallback = (e) => {
    root.removeEventListener(transitionEvent, transitionEndCallback);
    root.classList.remove('transitioning');
}

function updateQueryStringParameter(param, val) {
    var searchParams = new URLSearchParams(window.location.search);

    if ('URLSearchParams' in window) {
        if (val === "") {
            searchParams.delete(param);
        } else {
            searchParams.set(param, val);
        }
        var newRelativePathQuery = window.location.pathname + '?' + searchParams.toString();
        history.pushState(null, '', newRelativePathQuery);
    }
}

function clearQueryStringParameter() {
    var searchParams = new URLSearchParams(window.location.search);

    if ('URLSearchParams' in window) {
        var newRelativePathQuery = window.location.pathname;
        history.pushState(null, '', newRelativePathQuery);
    }
}

function appendSelectboxStateClass(select, val) {
    if (val !== "") {
        select.addClass('changed');
    } else {
        select.removeClass('changed');
    }
}

function replaceUnitText(text) {
    var item_unit = flat_view ? '譜面' : '曲';
    return text.replace("unit", item_unit);
}

// $("#hide-notice-btn").on("click", function(){    
//     $('.notice-wrap').removeClass('visible');
//     localStorage.setItem("noticeNewAddress", $('.notice-wrap').is(':visible'));
// });

$(document).ready(function() {
    if ('URLSearchParams' in window) {
        updateChartLevelSelectboxValue(searchParams);
    }
    $('html').removeClass('page-loading');

    // fetch('https://api.github.com/repos/zvuc/ongeki-db/commits?per_page=1')
    //     .then(res => res.json())
    //     .then(res => {
    //         let commitDateTime = new Date(res[0].commit.committer.date);
    //         let commitMsg = res[0].commit.message;
    //         // if multi-line commit message
    //         if(commitMsg.split('\n')[1] !== undefined) {
    //             document.getElementById('latest-commit-content').innerHTML = commitMsg.split('\n').slice(2).join('<br>');
    //         } else {
    //             document.getElementById('latest-commit-content').innerHTML = commitMsg;
    //         }
    //         document.getElementById('latest-commit').setAttribute('href', res[0].html_url);
    //         document.getElementById('latest-commit-date').innerHTML = commitDateTime.toISOString().split('T')[0]
    // })

    // localStorage.noticeNewAddress == "false" ? '' : $('.notice-wrap').addClass('visible');
    
    // google analytics
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'UA-141271073-1');
    gtag('config', 'G-YZ8GJR7QFL');

});
