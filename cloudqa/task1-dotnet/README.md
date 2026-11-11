# Task 1: Resilient Form Automation (C# / .NET / Selenium)

Automates form verification across dynamically changing web pages without relying on fixed XPath or CSS selectors. Evaluated against the CloudQA practice page across 17 distinct form contexts.

## Architecture

![Task 1 execution flow](../assets/task1-flow.svg)

### What each part does

1. **`Program.cs`**: Loads target URL and profile values from environment variables, sets Chrome options, and orchestrates execution.
2. **`FormAutomationService.cs`**: Discovers all distinct form containers in the document (standard `<form>` elements and shadow host custom elements) and recursively discovers and traverses iframes (standard, with ID, without ID, and nested inside shadow DOMs).
3. **`FieldInteractors.cs` & `IFieldInteractor.cs`**: Independent interactors for First Name, Gender, and State with scoped container isolation. Also populates additional present fields (Last Name, DOB, Mobile, Email, Country, Hobbies, About, Agreement).
4. **`ResilientEngineScripts.cs`**: Injected JavaScript engine executing tiered semantic discovery (ARIA labels, label associations, slots, names, placeholders, proximity fallback), interaction, and post-action value verification.

## Key Techniques

- **Semantic Multi-Tier Discovery**: Identifies controls via semantic attributes (`aria-label`, `<label for>`, enclosing labels, element name/id, slots, placeholders) rather than brittle positional selectors.
- **Deep Open Shadow DOM Traversal**: Recursively traverses open shadow roots up to arbitrary nesting depth (tested through 6 nested shadow levels).
- **Comprehensive Iframe Traversal**: Discovers and switches to light-DOM iframes (with ID and without ID) and deeply nested iframes residing inside Shadow DOM hosts (e.g. `<nestedshadow-iframe>`).
- **Post-Action Verification**: Every interaction is confirmed by querying element state (`.value`, `.checked`, or dropdown selection verification).

## How to Run

Requires .NET SDK 10 and Google Chrome.

```powershell
cd task1-dotnet
$env:TARGET_URL = "https://app.cloudqa.io/home/AutomationPracticeForm"
$env:FIRST_NAME = "Vaishnav"
$env:GENDER = "Male"
$env:STATE = "India"
$env:HEADLESS = "0"   # "0" for headed browser, "1" for headless
$env:KEEP_OPEN = "1"  # "1" to pause before closing Chrome

dotnet run
```

## Scope and Limitations

- **Open vs. Closed Shadow DOM**: Only open Shadow DOM roots (`mode: "open"`) can be inspected via JavaScript and Selenium. Closed shadow roots are inaccessible by browser security design.
- **Cross-Origin Iframes**: Traversal is supported for same-origin and accessible frames. Cross-origin frames with strict `X-Frame-Options` or CSP restrictions require browser-level CDP intervention.
- **Custom Dropdowns**: Supports native `<select>` and standard accessible combobox patterns (`role="combobox"` / `aria-haspopup="listbox"`). Bespoke canvas or non-standard custom widgets require custom interaction handlers.
