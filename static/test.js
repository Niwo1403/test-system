// SurveyJS library initialisation & constants
Survey.StylesManager.applyTheme("modern");
const defaultLocale = "en";
const surveyLocalization = Survey.surveyLocalization.locales[defaultLocale];  // surveyLocalization.pagePrevText, surveyLocalization.pageNextText
const originalCompleteText = surveyLocalization.completeText;
surveyLocalization.completeText = "Next";


// tests & site state:
let personalDataAnswerId = null;
let tests = null;
let pre_collect_index = 0;


function displayError(responseText) {
    document.getElementById("test-element").style.display = "none";
    document.getElementById("error-msg").innerHTML = responseText;
    document.getElementById("error-frame").style.display = "block";
}

function loadTestForPassedToken() {
    if (INITIAL_TOKEN === null) {
        displayError("Token missing.");
    } else {
        const xhr = new XMLHttpRequest();
        xhr.onload = function() {
            if (this.status === 200) {
                tests = JSON.parse(this.responseText);
                startTests();
            } else {
                displayError(this.responseText);
            }
        }
        xhr.open("GET", buildApiUrl("tests/", true), true);
        xhr.send();
    }
}

function loadTestForTokenCreation() {
    const xhr = new XMLHttpRequest();
    xhr.onload = function() {
        if (this.status === 200) {
            const tokenCreationTest = {description: JSON.parse(this.responseText), name: "create-token"};
            surveyLocalization.completeText = "Create token";
            displaySurvey(tokenCreationTest, postToken);
        } else {
            displayError(this.responseText);
        }
    }
    xhr.open("GET", buildApiUrl("token-creator-json/"), true);
    xhr.send();
}

function postToken(jsonAnswer, _) {
    postAnswer(buildApiUrl("token/"), jsonAnswer, showCreatedToken);
}

function showCreatedToken(token) {
    document.getElementById("test-element").style.display = "none";
    document.getElementById("test-result").style.display = "block";
    document.getElementById("token").innerHTML = token;
    const directLink = new URL(buildUrl("index.html", false, {"token": token}),
        document.baseURI).href;
    const directLinkA = document.getElementById("direct-link");
    directLinkA.href = directLink;
    directLinkA.innerHTML = directLink;
}


function startTests() {
    const personal_data_test = tests["personal_data_test"];
    displaySurvey(personal_data_test, postPersonalDataAnswer);
}

function displaySurvey(test, respHandler) {
	window.survey = new Survey.Model(test.description);
    survey.locale = defaultLocale;
	survey.onComplete.add(function (sender) {
        respHandler(sender.data, test.name);
    });
	survey.render("test-element");
}

/** Used after personal data was collected, to load pre collect or exportable test. */
function displayNextSurvey() {
    const pre_collect_tests = tests["pre_collect_tests"];
    if (pre_collect_index >= pre_collect_tests.length) {
        surveyLocalization.completeText = originalCompleteText;
        displaySurvey(tests["exportable_test"], postExportableTest);
    } else {
        displaySurvey(pre_collect_tests[pre_collect_index], postPreCollectTest);
        pre_collect_index++;
    }
}


function postAnswer(route, jsonAnswer, onSuccess) {
    const xhr = new XMLHttpRequest();
    xhr.onload = function() {
        document.getElementById('test-element').innerHTML = "";
        if (this.status === 201) {
            onSuccess(this.responseText);
        } else {
            displayError(this.responseText);
        }
    }
    xhr.open("POST", route, true);
    document.getElementById('test-element').innerHTML = "Loading...";
    xhr.send(JSON.stringify(jsonAnswer));
}

function postPersonalDataAnswer(jsonAnswer, testName) {
    postAnswer(buildApiUrl("personal-data-answer/", true, {"test-name": testName}), jsonAnswer,
        function (responseText) {
        personalDataAnswerId = JSON.parse(responseText);
        displayNextSurvey();
    });
}

function postPreCollectTest(jsonAnswer, testName) {
    postAnswer(buildApiUrl("test-answer/", true,
            {"test-name": testName, "personal-data-answer-id": personalDataAnswerId}),
        jsonAnswer, function (_) { displayNextSurvey(); });
}

function postExportableTest(jsonAnswer, testName) {
    postAnswer(buildApiUrl("test-answer/", true,
            {"test-name": testName, "personal-data-answer-id": personalDataAnswerId}),
        jsonAnswer, function (responseText) {
        window.location.href = buildUrl("result.html", true,
            {"exportable-test-answer-id": responseText});
    });
    pre_collect_index = 0;
}
