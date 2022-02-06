let personId = null;
let tests = null;
let pre_collect_index = 0;

Survey.StylesManager.applyTheme("modern");


function displayError(responseText) {
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


function startTests() {
    const personal_data_test = tests["personal_data_test"];
    displaySurvey(personal_data_test, postPerson);
}

function displaySurvey(test, respHandler) {
	window.survey = new Survey.Model(test.description);
	survey.onComplete.add(function (sender) {
        respHandler(sender.data, test.name);
    });
	survey.render("test-element");
}

/** Used after personal data was collected, to load pre collect or evaluable test. */
function displayNextSurvey() {
    const pre_collection_tests = tests["pre_collection_tests"];
    if (pre_collect_index >= pre_collection_tests.length) {
        displaySurvey(tests["evaluable_test"], postEvaluableTest);
    } else {
        displaySurvey(pre_collection_tests[pre_collect_index], postPreCollectTest);
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

function postPerson(jsonAnswer, _) {
    postAnswer(buildApiUrl("person/", true), jsonAnswer, function (responseText) {
        personId = JSON.parse(responseText);
        displayNextSurvey();
    });
}

function postPreCollectTest(jsonAnswer, testName) {
    postAnswer(buildApiUrl("test-answer/", false,
            {"test-name": testName, "person-id": personId}),
        jsonAnswer, function (_) { displayNextSurvey(); });
}

function postEvaluableTest(jsonAnswer, testName) {
    postAnswer(buildApiUrl("test-answer/", false, {"test-name": testName, "person-id": personId}),
        jsonAnswer, function (responseText) {
        window.location.href = buildUrl("result.html", true,
            {"evaluable-test-answer-id": responseText});
    });
    pre_collect_index = 0;
}
