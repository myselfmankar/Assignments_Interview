# CloudQA Practical Assessment

Two independent implementations for the CloudQA assessment. Both automate browsers with Selenium without relying on fragile fixed XPath or CSS selectors.

![CloudQA architecture overview](assets/cloudqa-overview.svg)

## How the two tasks relate

| | Task 1 | Task 2 |
|---|---|---|
| Purpose | Fill and verify known form fields across standard DOM, multi-level Shadow DOMs, and nested iframes | Turn a plain-English test case into an automated browser workflow |
| Stack | C#, .NET 10, Selenium | Python, Gemini, Selenium |
| Planning | Configurable profile from environment variables | Gemini generates a structured JSON action plan |
| Execution | Scoped field interactors + tiered resilient JavaScript locator engine | Python action executor + semantic JavaScript locator engine |
| Output | Per-context verification summary across 17 DOM/shadow/iframe contexts | Step-by-step verification, PASS / FAIL report, and failure screenshots |

> **Important:** Task 2 does not import, call, or reuse Task 1's C# classes. The implementations share an architectural philosophy—resilient semantic discovery and verification—not code.

---

## Repository Layout

- [`task1-dotnet/`](task1-dotnet/) — C# .NET resilient form automation for all DOM, nested Shadow DOM, and iframe contexts.
- [`task2-agent/`](task2-agent/) — Natural-language browser testing agent powered by Gemini and Selenium.
- [`assets/`](assets/) — Architecture and execution flow diagrams.

---

## Quick Start

### Task 1 — C# / Selenium (.NET 10)

Requires .NET SDK 10 and Google Chrome.

```powershell
cd task1-dotnet
$env:TARGET_URL = "https://app.cloudqa.io/home/AutomationPracticeForm"
$env:FIRST_NAME = "Vaishnav"
$env:GENDER = "Male"
$env:STATE = "India"
$env:HEADLESS = "0"  # Set to "1" for headless execution, "0" for visible browser
$env:KEEP_OPEN = "1" # Set to "1" to pause before closing browser

dotnet run
```

### Task 2 — Python / Gemini / Selenium

Requires Python 3.10+, Google Chrome, and a Gemini API key.

```powershell
cd task2-agent
pip install -r requirements.txt
$env:GEMINI_API_KEY = "your-api-key"

python agent.py --url https://phptravels.com/demo --test "Verify that the demo request form is displayed with First Name, Last Name, Business Name and Email fields" --headed
```

---

## Detailed Guides

- [Task 1 Architecture, Setup, and Limitations](task1-dotnet/README.md)
- [Task 2 Architecture, Setup, and Limitations](task2-agent/README.md)
