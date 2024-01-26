const colorSchemeInput = document.querySelectorAll('input[name="colorScheme"]');
const langOptionInput = document.querySelectorAll('input[name="siteLanguage"]');
const gameRegionChecks = document.querySelectorAll('input[name="gameRegion"]');
const gameRegionQuickSwitch = document.getElementById('gameRegionQuickSwitch');
let userLanguage = localStorage.getItem('userLanguage');
let cachedTranslations = localStorage.getItem('translations');

// Check if the userGameRegion value is nonexistent, create one with the default value 'jp'
let currentRegion = localStorage.getItem('userGameRegion');
if (!currentRegion) {
  localStorage.setItem('userGameRegion', 'jp');
}
// Check the initial game region
const initialGameRegion = currentRegion || 'jp';
document.querySelector(`input[value="${initialGameRegion}"]`).checked = true;
gameRegionQuickSwitch.checked = (initialGameRegion === 'jp' ? false : true);
document.documentElement.setAttribute('data-game-region', currentRegion);
// switchGameRegion(); // Apply initial region



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

function loadTranslations() {
  return new Promise((resolve, reject) => {
    fetch('../shared/translations/translations.json')
      .then(response => response.json())
      .then(translations => {
        // Cache
        sessionStorage.setItem('translations', JSON.stringify(translations));
        resolve();  // Resolve the promise after successfully loading translations
      })
      .catch(error => {
        console.error('Error loading translations:', error);
        reject(error);  // Reject the promise in case of an error
      });
  });
}

function getTranslation(languageCode, keyName) {
  const cachedTranslations = sessionStorage.getItem('translations');
  // console.log(`${languageCode} / ${keyName}`);
  // console.log(`cachedTranslations: ${cachedTranslations ? 'true' : 'false'}`);

  if (cachedTranslations) {
    // If available, get translation from the cached data
    const translations = JSON.parse(cachedTranslations);

    if (translations[languageCode] && translations[languageCode][keyName]) {
      return translations[languageCode][keyName];
    }
  }
}

function applyTranslations(translations, languageCode) {
  // Set the language
  const currentLanguage = translations[languageCode];

  // Find all elements with data-translation attribute
  const elements = document.querySelectorAll('[data-i18n]');

  // Update content for each element based on the language
  elements.forEach(element => {
    const key = element.getAttribute('data-i18n');
    if (currentLanguage[key]) {
      element.innerText = currentLanguage[key];
    }
  });
}

function setLanguage(e) {
  const languageCode = document.querySelector('input[name="siteLanguage"]:checked').value;
  const languageSettingsWrapper = document.querySelector('#site-menu .menu-list-item.lang-settings');

  if (e) {
    languageSettingsWrapper.classList.add('setting-changed');
  }

  // Save the selected language in localStorage
  localStorage.setItem('userLanguage', languageCode);

  // Apply the selected language with a transition effect
  document.documentElement.setAttribute('data-lang', languageCode);

  applyTranslations(JSON.parse(cachedTranslations), languageCode);
  return Promise.resolve(); // Return a resolved Promise for consistency
}

function initTranslations() {
  if (!userLanguage) {
    localStorage.setItem('userLanguage', 'ja');
    userLanguage = 'ja';
    // console.log('initialized userLanguage to ja');
  }

  if (!cachedTranslations) {
  // Load translations from JSON
  return loadTranslations()
    .then(() => {
      // Update cachedTranslations after loading translations
      cachedTranslations = sessionStorage.getItem('translations');
      applyTranslations(JSON.parse(cachedTranslations), userLanguage);
    })
    .catch(error => console.error('Error setting language:', error));
  }

}

