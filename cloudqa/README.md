# CloudQA Practical Assessment: Resilient Web Automation & AI Test Agent

This repository contains production-ready solutions for both tasks of the CloudQA evaluation.

---

## 📂 Repository Structure

- [`task1-dotnet/`](task1-dotnet/): **Adaptive Form Automation (C# & Selenium 4)**
  - Self-healing automation for dynamic web forms.
  - Handles mutations in attributes, layout reordering, and boundary obstacles (Root DOM, open Shadow DOMs, deeply nested shadow roots 1–6, and IFrames with or without IDs).
- [`task2-agent/`](task2-agent/): **Plain-English Automated Browser Test Agent (Python, Selenium & Gemini)**
  - Translates unstructured plain-English test instructions into autonomous browser execution plans.
  - Zero hardcoding; works dynamically across unseen websites (`phptravels.com/demo`, `example.com`, etc.).
  - Reuses Task 1's deep Shadow DOM piercer, semantic accessibility locator, and spatial proximity engine for reliable execution.

---

## 🛠️ Quick Start

### Task 1: Resilient Form Automation (C# .NET)
```powershell
# Run against CloudQA Practice Form
dotnet run --project task1-dotnet
```
*Configurable via environment variables: `TARGET_URL`, `FIRST_NAME`, `GENDER`, `STATE`, `HEADLESS`.*

### Task 2: Plain-English Browser Agent (Python)
```powershell
# 1. Install dependencies
cd task2-agent
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
