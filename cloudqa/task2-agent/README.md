# Task 2: Plain-English Automated Browser Test Agent

Give the agent a test instruction in plain English. It inspects the page, asks Gemini to produce a structured action plan, executes that plan in Chrome, and checks whether the expected result appeared.

## Architecture

![Task 2 agent pipeline](../assets/task2-flow.svg)

### Execution flow

1. **Input:** receive a target URL and plain-English test case.
2. **Snapshot:** inspect visible controls and page context, including accessible open Shadow DOM and nested frames.
3. **Planning:** Gemini returns a JSON list of browser actions.
4. **Validation:** reject malformed plans, unsupported actions, missing targets/values, and plans without assertions.
5. **Execution:** Python runs the allow-listed actions using Selenium and its own semantic JavaScript locator.
6. **Verification:** check step assertions and the final success condition. Report PASS / FAIL; save a timestamped screenshot on failure.

> Task 2 does not use Task 1's C# implementation. Its locator and executor are implemented independently in `agent.py`.

## Tech stack

- **Python 3.10+**
- **Selenium WebDriver** with Chrome
- **Google Gemini** through the official `google-genai` SDK
- **python-dotenv** for local environment configuration

## Run

### 1. Install dependencies

```bash
cd cloudqa/task2-agent
pip install -r requirements.txt
```

### 2. Set the Gemini API key

Windows PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
```

Or put it in a local `.env` file in this directory.

### 3. Start a test

```bash
python agent.py --url https://phptravels.com/demo --test "Verify that the demo request form is displayed with First Name, Last Name, Business Name and Email fields"
```

Add `--headed` to show the browser window.

### Customer meeting demo runner

The optional `test_login_and_schedule.py` runner uses environment variables for credentials. Set these locally before running it:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
$env:CUSTOMER_EMAIL = "your-test-account-email"
$env:CUSTOMER_PASSWORD = "your-test-account-password"
python test_login_and_schedule.py
```

The prompt sends credential placeholders to Gemini; the actual values are inserted into the returned plan locally. Do not commit real credentials or put them in prompts, screenshots, logs, or source files. If credentials were previously committed, rotate them immediately; removing them in a later commit does not erase them from Git history.

## Tests

The deterministic planner-contract tests do not launch Chrome or call Gemini:

```bash
pip install pytest
pytest -q
```

For an end-to-end run, Chrome, a valid Gemini API key, internet access and available API quota are required.

## Scope and limitations

The agent supports the standard DOM, accessible open Shadow DOM and nested iframes up to four levels. Closed shadow roots, inaccessible cross-origin content, canvas-only controls and custom widgets without discoverable accessible options cannot be reliably automated. The generated plan is restricted to allow-listed browser actions; avoid running tests that could trigger irreversible actions on real accounts or production systems.
