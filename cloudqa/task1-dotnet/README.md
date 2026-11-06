# Task 1: Resilient Form Automation

## Problem Statement
Automate testing for **First Name** (text box), **Gender** (radio button), and **State** (dropdown) on `app.cloudqa.io/home/AutomationPracticeForm`. The automation is designed to remain functional under these controlled page changes:
- Field order, IDs, names, or CSS classes mutate.
- The form is enclosed within the standard DOM, open Shadow DOMs, or nested IFrames (with or without IDs; frame traversal is bounded to four levels).
- Elements are replaced with custom UI widgets or have missing explicit label bindings.
- The target URL is changed to alternate versions of the page.

---


### Key Mechanisms
1. **Semantic & Accessibility-First Resolution:**
   Rather than binding to brittle selectors (fixed XPaths or IDs), elements are identified via computed accessibility roles (`textbox`, `radio`, `combobox`), associated text labels (`<label>`, `aria-label`, `placeholder`), and token similarity.
2. **Open Shadow DOM Traversal:**
   Recursively searches accessible open shadow roots without hardcoding shadow host selectors. Closed shadow roots are not accessible through this approach.
3. **Multi-Context Discovery (IFrames):**
   Enumerates frames without relying on their IDs and recursively searches nested frames up to a maximum depth of four.
4. **Spatial Geometry Proximity Fallback:**
   When DOM hierarchy and attributes are scrambled, elements are resolved using bounding-box screen coordinates (`getBoundingClientRect()`) relative to their visual labels.
5. **Synthetic Event Dispatching:**
   Complements native Selenium interactions with synthetic DOM events (`focus`, `input`, `change`) to guarantee updates register across modern reactive frameworks.

## Requirements and setup

- .NET SDK 10.0
- Google Chrome (Selenium Manager resolves the matching driver)

From the repository root, run in PowerShell:

```powershell
$env:TARGET_URL = "https://app.cloudqa.io/home/AutomationPracticeForm"
$env:FIRST_NAME = "Vaishnav"
$env:GENDER = "Male"
$env:STATE = "Maharashtra"
$env:HEADLESS = "0" # Set to 1 or omit for headless mode

dotnet run --project .\cloudqa\task1-dotnet\AdaptiveFormAutomation.csproj
```

The program reports success only for a context where all three fields were located and verified. It fails the run if no complete form context passes. The current implementation supports native selects and custom dropdowns whose opened options are exposed in the accessible DOM; highly bespoke widgets may require an adapter.
