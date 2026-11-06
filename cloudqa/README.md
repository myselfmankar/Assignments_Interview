# CloudQA Practical Assessment: Resilient Web Automation & AI Test Agent

This repository contains assessment implementations for both tasks of the CloudQA evaluation.

---

## 📂 Repository Structure

- [`task1-dotnet/`](task1-dotnet/): **Adaptive Form Automation (C# & Selenium 4)**
  - Semantic, verification-driven automation for dynamic web forms.
  - Handles attribute and layout changes across the standard DOM, accessible open Shadow DOMs, and nested IFrames (bounded to four frame levels).
- [`task2-agent/`](task2-agent/): **Plain-English Automated Browser Test Agent (Python, Selenium & Gemini)**
  - Translates unstructured plain-English test instructions into autonomous browser execution plans.
  - Uses an LLM-generated, allow-listed action plan and semantic element matching; compatibility depends on each site's accessible DOM.
  - Uses semantic element matching, open Shadow DOM traversal, and recursive iframe discovery (bounded to four levels).

---

## 🛠️ Quick Start

### Task 1: Resilient Form Automation (C# .NET)
```powershell
# Run against CloudQA Practice Form
dotnet run --project cloudqa/task1-dotnet/AdaptiveFormAutomation.csproj
```
*Configurable via environment variables: `TARGET_URL`, `FIRST_NAME`, `GENDER`, `STATE`, `HEADLESS`.*

### Task 2: Plain-English Browser Agent (Python)
```powershell
# 1. Install dependencies
cd cloudqa/task2-agent
pip install -r requirements.txt

# 2. Set your Gemini API key
$env:GEMINI_API_KEY="your-api-key"

# 3. Run test on PHPTRAVELS demo site
python agent.py --url https://phptravels.com/demo --test "Verify that the demo request form is displayed with First Name, Last Name, Business Name and Email fields"
```

---

## 📖 Detailed Documentation
- For Task 1 architectural details, see [task1-dotnet/README.md](task1-dotnet/README.md).
- For Task 2 agent architecture and options, see [task2-agent/README.md](task2-agent/README.md).

## Prerequisites

- Task 1: .NET SDK 10.0 and Google Chrome.
- Task 2: Python 3.10+, Google Chrome, and a Gemini API key for end-to-end execution.

See each task README for exact setup commands, supported page structures, test strategy, and limitations. The implementations are assessment prototypes, not universal or production-certified automation frameworks.
