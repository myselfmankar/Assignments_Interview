# Task 1: Resilient Form Automation

## Problem Statement
Automate testing for **First Name** (text box), **Gender** (radio button), and **State** (dropdown) on `app.cloudqa.io/home/AutomationPracticeForm`. The automation must remain functional even if:
- Field order, IDs, names, or CSS classes mutate.
- The form is enclosed within standard DOM, open Shadow DOMs (including deeply nested levels), or IFrames (with or without IDs).
- Elements are replaced with custom UI widgets or have missing explicit label bindings.
- The target URL is changed to alternate versions of the page.

---


### Key Mechanisms
1. **Semantic & Accessibility-First Resolution:**
   Rather than binding to brittle selectors (fixed XPaths or IDs), elements are identified via computed accessibility roles (`textbox`, `radio`, `combobox`), associated text labels (`<label>`, `aria-label`, `placeholder`), and token similarity.
2. **Universal Shadow DOM Traversal:**
   Recursively penetrates open shadow roots at arbitrary nesting depths to access web components without hardcoding shadow host selectors.
3. **Multi-Context Discovery (IFrames):**
   Automatically enumerates and navigates browsing contexts, supporting anonymous iframes, iframes with IDs, and nested frames.
4. **Spatial Geometry Proximity Fallback:**
   When DOM hierarchy and attributes are scrambled, elements are resolved using bounding-box screen coordinates (`getBoundingClientRect()`) relative to their visual labels.
5. **Synthetic Event Dispatching:**
   Complements native Selenium interactions with synthetic DOM events (`focus`, `input`, `change`) to guarantee updates register across modern reactive frameworks.
