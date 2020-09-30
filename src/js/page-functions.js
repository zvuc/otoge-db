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

$(document).ready(function() {
    $('html').removeClass('page-loading');
});