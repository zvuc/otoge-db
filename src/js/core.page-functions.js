// theme switcher
const toggleSwitch = document.getElementById('themeToggleCheckbox');
const root = document.documentElement;

if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    toggleSwitch.checked = false;
    root.setAttribute('data-theme', 'dark');
}

if (window.matchMedia('(prefers-color-scheme: light)').matches) {
    toggleSwitch.checked = true;
    root.setAttribute('data-theme', 'light');
}

whichTransitionEvent = () => {
    let t,
        el = document.createElement("fakeelement");

    let transitions = {
        "transition"      : "transitionend",
        "OTransition"     : "oTransitionEnd",
        "MozTransition"   : "transitionend",
        "WebkitTransition": "webkitTransitionEnd"
    }

    for (t in transitions){
        if (el.style[t] !== undefined){
            return transitions[t];
        }
    }
}

let transitionEvent = whichTransitionEvent(),
    item = document.querySelector('.circle'),
    message = document.querySelector('.footer'),
    counter = 1;

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
      return str.replace(/(^|[^\\])(\\\\)*\\$/, "$&\\") ;
  } else {
      return str;
  }
}

function appendSelectboxStateClass(select, val) {
    if (val !== "") {
        select.addClass('changed');
    } else {
        select.removeClass('changed');
    }
}

// $("#hide-notice-btn").on("click", function(){    
//     $('.notice-wrap').removeClass('visible');
//     localStorage.setItem("noticeNewAddress", $('.notice-wrap').is(':visible'));
// });


$(document).ready(function() {
    $('html').removeClass('page-loading');

    fetch('https://api.github.com/repos/zvuc/ongeki-db/commits?per_page=1')
        .then(res => res.json())
        .then(res => {
            let commitDateTime = new Date(res[0].commit.committer.date);
            document.getElementById('latest-commit-content').innerHTML = res[0].commit.message;
            document.getElementById('latest-commit').setAttribute('href', res[0].html_url);
            document.getElementById('latest-commit-date').innerHTML = commitDateTime.toISOString().split('T')[0]
    })

    // localStorage.noticeNewAddress == "false" ? '' : $('.notice-wrap').addClass('visible');
});
