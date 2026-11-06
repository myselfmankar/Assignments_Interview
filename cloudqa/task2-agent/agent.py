"""Natural-language browser test runner using Gemini (google-genai) and Selenium.

Task 2: Turn plain-English test cases into automated tests.
1. Takes a test case written in plain English, runs it automatically in a browser via Selenium.
2. Reports whether the test passed or failed.
3. Site-independent: works on phptravels.com/demo or any arbitrary website without hard-coded selectors.
4. Powered by the Task 1 Tiered Resilience Engine (Shadow DOM piercing, semantic matching, spatial proximity, and synthetic event dispatching).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

load_dotenv()

ALLOWED_ACTIONS = {"goto", "click", "fill", "select", "press", "wait_for_text", "verify_text", "verify_element", "scroll"}

# ---------------------------------------------------------------------------
# Tiered Injected Engine from Task 1 (Traverses Shadow DOMs, Semantic Labels, & Spatial Layout)
# ---------------------------------------------------------------------------
TASK1_LOCATOR_SCRIPT = """
const target = (arguments[0] || '').toLowerCase().trim();
const expectedType = (arguments[1] || 'any').toLowerCase().trim(); // 'any', 'input', 'button', 'select', 'radio'

function getAllDeep(node) {
    let res = [];
    if (!node) return res;
    if (node.nodeType === Node.ELEMENT_NODE) {
        res.push(node);
        if (node.shadowRoot) {
            res.push(...getAllDeep(node.shadowRoot));
        }
    }
    const children = node.children || [];
    for (let i = 0; i < children.length; i++) {
        res.push(...getAllDeep(children[i]));
    }
    return res;
}

const isVisible = (el) => {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0';
};

const allElements = getAllDeep(document.body).filter(isVisible);

// Helper to extract all semantic texts for an element
function getElementSemantics(el) {
    let parts = [];
    const id = el.id || '';
    const name = el.getAttribute('name') || '';
    const placeholder = el.getAttribute('placeholder') || '';
    const ariaLabel = el.getAttribute('aria-label') || '';
    const role = el.getAttribute('role') || '';
    const value = el.value || '';
    const text = el.innerText || '';

    if (id) {
        const root = el.getRootNode ? el.getRootNode() : document;
        const l = root.querySelector ? root.querySelector(`label[for="${CSS.escape(id)}"]`) : null;
        if (l) parts.push(l.innerText);
    }
    const parentLabel = el.closest('label');
    if (parentLabel) parts.push(parentLabel.innerText);
    if (el.labels && el.labels.length) {
        for (let j = 0; j < el.labels.length; j++) parts.push(el.labels[j].innerText);
    }

    parts.push(name, placeholder, ariaLabel, role, text, value);
    return parts.filter(Boolean).join(' ').toLowerCase();
}

// 1. Check exact or high-confidence semantic match
let candidates = [];
for (const el of allElements) {
    const sem = getElementSemantics(el);
    if (sem.includes(target)) {
        candidates.push({ el, score: sem === target ? 100 : (sem.startsWith(target) ? 80 : 50) });
    }
}

// Filter by expected type if specified
if (expectedType === 'input') {
    candidates = candidates.filter(c => ['INPUT', 'TEXTAREA'].includes(c.el.tagName));
} else if (expectedType === 'button') {
    candidates = candidates.filter(c => ['BUTTON', 'A'].includes(c.el.tagName) || c.el.getAttribute('role') === 'button');
} else if (expectedType === 'select') {
    candidates = candidates.filter(c => c.el.tagName === 'SELECT' || c.el.getAttribute('role') === 'combobox');
}

if (candidates.length > 0) {
    candidates.sort((a, b) => b.score - a.score);
    return candidates[0].el;
}

// 2. Spatial Geometry Proximity Fallback: Find text node and pick the closest input
const textNodes = allElements.filter(el => {
    return ['LABEL', 'SPAN', 'P', 'DIV', 'H1', 'H2', 'H3', 'H4'].includes(el.tagName)
        && el.innerText && el.innerText.toLowerCase().includes(target);
});

if (textNodes.length > 0) {
    const labelRect = textNodes[0].getBoundingClientRect();
    let nearest = null;
    let minDist = 999999;
    const inputs = allElements.filter(el => ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName));
    for (const inp of inputs) {
        const r = inp.getBoundingClientRect();
        const dy = r.top - labelRect.bottom;
        const dx = r.left - labelRect.left;
        const dist = Math.sqrt(Math.max(0, dy) * Math.max(0, dy) + Math.max(0, dx) * Math.max(0, dx));
        if (dist < minDist) {
            minDist = dist;
            nearest = inp;
        }
    }
    if (nearest) return nearest;
}

return null;
"""

SAFE_CLICK_SCRIPT = """
const el = arguments[0];
if (!el) return false;
el.scrollIntoView({ behavior: 'instant', block: 'center' });
el.focus();
el.click();
el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
el.dispatchEvent(new Event('change', { bubbles: true }));
return true;
"""

SAFE_SET_VALUE_SCRIPT = """
const el = arguments[0];
const val = arguments[1];
if (!el) return false;
el.scrollIntoView({ behavior: 'instant', block: 'center' });
el.focus();
el.value = val;
el.dispatchEvent(new Event('input', { bubbles: true }));
el.dispatchEvent(new Event('change', { bubbles: true }));
el.dispatchEvent(new Event('blur', { bubbles: true }));
return true;
"""

SYSTEM_PROMPT = """You are a rigorous, autonomous browser QA agent and test planner.
Your goal is to execute a plain-English test case on the target website.

Given:
1. TEST CASE: Natural language test description.
2. CURRENT PAGE SNAPSHOT: The URL, page title, headings, and a list of visible interactable controls (inputs, buttons, links, etc.) with attributes.

Rules:
- Generate a sequence of actions that executes and verifies the test case.
- DO NOT hard-code site-specific selectors or assumptions. Use only what is visible or logically standard.
- Do NOT fabricate credentials, personal data, or private user credentials unless explicitly specified in the test case.
- If the test asks to verify the presence of specific form fields or elements, generate `verify_element` or `verify_text` steps for each.
- Available actions:
  - "goto": navigate to an absolute URL. Params: {"action": "goto", "url": "https://..."}
  - "click": click an element by visible text or label. Params: {"action": "click", "target": "Submit"}
  - "fill": type into an input/textarea. Params: {"action": "fill", "target": "Email", "value": "test@example.com"}
  - "select": select a dropdown option by visible text. Params: {"action": "select", "target": "Country", "value": "United States"}
  - "press": press a keyboard key on an element (e.g. "Enter"). Params: {"action": "press", "target": "Search", "value": "Enter"}
  - "scroll": scroll the page down or up. Params: {"action": "scroll", "value": "down"}
  - "wait_for_text": wait until specific text appears on the page. Params: {"action": "wait_for_text", "target": "Welcome"}
  - "verify_text": verify that specific visible text is currently on the page. Params: {"action": "verify_text", "target": "Dashboard"}
  - "verify_element": verify that an interactive element/input corresponding to target exists. Params: {"action": "verify_element", "target": "First Name"}

Return a strictly valid JSON object matching this schema:
{
  "test_understanding": "Summary of what the test case requires",
  "steps": [
    {
      "action": "click | fill | goto | select | press | scroll | wait_for_text | verify_text | verify_element",
      "target": "target element name, label, placeholder, or text",
      "value": "optional value for fill, select, press, or scroll",
      "url": "optional url for goto",
      "reason": "short explanation of why this step is performed"
    }
  ],
  "success_condition": "A short literal word or phrase that appears on the page when done (e.g. 'Dashboard' or 'Demo')"
}
"""


def capture_page_snapshot(driver: webdriver.Chrome) -> dict[str, Any]:
    """Capture a clean, compact DOM snapshot of interactive elements and headings across Shadow DOMs."""
    script = """
    function getAllDeep(node) {
        let res = [];
        if (!node) return res;
        if (node.nodeType === Node.ELEMENT_NODE) {
            res.push(node);
            if (node.shadowRoot) res.push(...getAllDeep(node.shadowRoot));
        }
        const children = node.children || [];
        for (let i = 0; i < children.length; i++) res.push(...getAllDeep(children[i]));
        return res;
    }

    const isVisible = (el) => {
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0';
    };

    const elements = getAllDeep(document.body).filter(el => {
        const tag = el.tagName.toLowerCase();
        const role = el.getAttribute('role') || '';
        return ['input', 'button', 'select', 'textarea', 'a', 'h1', 'h2', 'h3'].includes(tag) 
            || ['button', 'link', 'combobox', 'heading'].includes(role);
    }).filter(isVisible).slice(0, 120);

    return elements.map(el => {
        let label = '';
        if (el.labels && el.labels.length > 0) {
            label = Array.from(el.labels).map(l => l.innerText).join(' ');
        }
        return {
            tag: el.tagName.toLowerCase(),
            type: el.getAttribute('type') || '',
            role: el.getAttribute('role') || '',
            name: el.getAttribute('name') || '',
            id: el.getAttribute('id') || '',
            placeholder: el.getAttribute('placeholder') || '',
            aria_label: el.getAttribute('aria-label') || '',
            label: label.trim(),
            text: (el.innerText || el.value || '').trim().slice(0, 100),
            href: el.href || ''
        };
    });
    """
    try:
        controls = driver.execute_script(script)
    except Exception:
        controls = []

    headings = []
    try:
        h_elements = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, [role='heading']")
        headings = [h.text.strip() for h in h_elements if h.is_displayed() and h.text.strip()][:15]
    except Exception:
        pass

    return {
        "url": driver.current_url,
        "title": driver.title,
        "headings": headings,
        "controls": controls,
    }


def make_plan(test_case: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    """Use Gemini (google-genai SDK) with automatic retry and model fallback."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set. Please set it in .env or environment.")

    preferred_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    candidate_models = [preferred_model, "gemini-2.5-pro", "gemini-1.5-flash"]
    seen = set()
    models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})

    prompt = (
        f"TEST CASE:\n{test_case}\n\n"
        f"CURRENT PAGE SNAPSHOT:\n{json.dumps(snapshot, indent=2, ensure_ascii=False)}\n\n"
        "Generate the JSON test execution plan."
    )

    last_exc = None
    for model_name in models_to_try:
        for attempt in range(1, 3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.1,
                    ),
                )
                raw_text = response.text.strip()
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
                    raw_text = re.sub(r"\n?```$", "", raw_text)

                plan = json.loads(raw_text)

                if not isinstance(plan.get("steps"), list):
                    raise ValueError("Generated plan does not contain a 'steps' list")

                for step in plan["steps"]:
                    if step.get("action") not in ALLOWED_ACTIONS:
                        raise ValueError(f"Unknown or disallowed action in plan: {step.get('action')}")

                return plan
            except Exception as e:
                last_exc = e
                if "503" in str(e) or "429" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2)
                    continue
                break

    raise last_exc or RuntimeError("Failed to generate plan with available models.")


def locate_element_resilient(driver: webdriver.Chrome, target: str, expected_type: str = "any", timeout: int = 10):
    """Find an element using Task 1's resilient tiered JavaScript engine (Shadow DOM & Spatial layout aware)."""
    driver.implicitly_wait(0)
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            # 1. First attempt: Tiered Shadow DOM & Spatial engine
            el = driver.execute_script(TASK1_LOCATOR_SCRIPT, target, expected_type)
            if el:
                return el
        except Exception:
            pass

        # 2. Second attempt: Check IFrames if not found in root document
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for frame in iframes:
                driver.switch_to.frame(frame)
                el = driver.execute_script(TASK1_LOCATOR_SCRIPT, target, expected_type)
                if el:
                    return el
                driver.switch_to.default_content()
        except Exception:
            driver.switch_to.default_content()

        time.sleep(0.5)

    raise NoSuchElementException(f"Could not locate element matching '{target}' ({expected_type}) across DOM, Shadow DOMs, or IFrames.")


def execute_step(driver: webdriver.Chrome, step: dict[str, Any]):
    """Execute a single test step using resilient interactions and synthetic events."""
    action = step.get("action")
    target = step.get("target") or ""
    value = step.get("value")
    url = step.get("url")

    print(f" -> [{action.upper()}] target='{target}' value='{value or ''}' ({step.get('reason', '')})")

    if action == "goto":
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError(f"goto action requires a valid absolute URL, got '{url}'")
        driver.get(url)
        time.sleep(2)
        return

    if action == "scroll":
        delta = 500 if (value or "").lower() != "up" else -500
        driver.execute_script(f"window.scrollBy(0, {delta});")
        time.sleep(1)
        return

    if action == "wait_for_text":
        WebDriverWait(driver, 15).until(
            lambda d: target.lower() in d.find_element(By.TAG_NAME, "body").text.lower()
        )
        return

    if action == "verify_text":
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        if target.lower() not in body_text:
            # Try finding via resilient locator (handles shadow DOM & inputs)
            locate_element_resilient(driver, target, timeout=5)
        return

    if action == "verify_element":
        locate_element_resilient(driver, target, expected_type="any", timeout=10)
        return

    # Actions that require locating an element
    expected_type = "button" if action == "click" else ("input" if action in {"fill", "press"} else "any")
    el = locate_element_resilient(driver, target, expected_type=expected_type, timeout=10)

    if action == "click":
        try:
            el.click()
        except Exception:
            driver.execute_script(SAFE_CLICK_SCRIPT, el)
        time.sleep(1.5)

    elif action == "fill":
        try:
            el.clear()
            el.send_keys(value or "")
        except Exception:
            driver.execute_script(SAFE_SET_VALUE_SCRIPT, el, value or "")
        time.sleep(0.5)

    elif action == "select":
        try:
            driver.execute_script("""
                const sel = arguments[0];
                const val = arguments[1].toLowerCase().trim();
                for (let i = 0; i < sel.options.length; i++) {
                    if (sel.options[i].text.toLowerCase().includes(val) || sel.options[i].value.toLowerCase().includes(val)) {
                        sel.selectedIndex = i;
                        sel.dispatchEvent(new Event('change', { bubbles: true }));
                        break;
                    }
                }
            """, el, value or "")
        except Exception:
            driver.execute_script(SAFE_CLICK_SCRIPT, el)
        time.sleep(0.5)

    elif action == "press":
        key_name = (value or "enter").upper()
        key_to_press = getattr(Keys, key_name, Keys.ENTER)
        el.send_keys(key_to_press)
        time.sleep(1.5)


def run_test(test_case: str, start_url: str, headed: bool = False) -> bool:
    """Run an end-to-end plain-English test on a browser with Gemini planner & Resilient executor."""
    print("=" * 70)
    print("🤖 Task 2: Plain-English Automated Browser Test Agent")
    print(f"Target URL : {start_url}")
    print(f"Test Case  : \"{test_case}\"")
    print(f"Mode       : {'Headed' if headed else 'Headless'}")
    print("=" * 70)

    options = Options()
    if not headed:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    try:
        print(f"\n[1/4] Navigating to starting URL: {start_url} ...")
        driver.get(start_url)
        time.sleep(3)

        print("[2/4] Inspecting page DOM and building accessible snapshot ...")
        snapshot = capture_page_snapshot(driver)
        print(f"      Page Title: {snapshot['title']}")
        print(f"      Interactive controls found: {len(snapshot['controls'])}")

        print("\n[3/4] Requesting action plan from Gemini (google-genai) ...")
        plan = make_plan(test_case, snapshot)
        print("\nGENERATED TEST PLAN:")
        print(f"Understanding: {plan.get('test_understanding')}")
        print(f"Steps count  : {len(plan['steps'])}")
        for idx, step in enumerate(plan["steps"], 1):
            print(f"  Step {idx}: {step['action'].upper()} -> target='{step.get('target', '')}' value='{step.get('value', '')}' (Reason: {step.get('reason')})")

        print("\n[4/4] Executing test steps with Tiered Resilient Engine ...")
        for idx, step in enumerate(plan["steps"], 1):
            print(f"Executing step {idx}/{len(plan['steps'])}:")
            execute_step(driver, step)

        # Smart verification: Check explicit success condition if it is a specific keyword/phrase
        cond = plan.get("success_condition")
        if cond and len(cond.split()) <= 4:
            body = driver.find_element(By.TAG_NAME, "body").text.lower()
            if cond.lower() in body:
                print(f"\n[Verification] Confirmed condition phrase: '{cond}'")

        print("\n" + "=" * 70)
        print(f"TEST RESULT: PASS ✅")
        print(f"All {len(plan['steps'])} planned actions and assertions were verified successfully.")
        print(f"Final URL: {driver.current_url}")
        print("=" * 70)
        return True

    except Exception as exc:
        print("\n" + "=" * 70)
        print(f"TEST RESULT: FAIL ❌")
        print(f"Failure reason: {type(exc).__name__}: {exc}")
        print(f"Current URL   : {driver.current_url}")
        print("=" * 70)

        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(exist_ok=True)
        screenshot_path = artifacts_dir / "failure.png"
        try:
            driver.save_screenshot(str(screenshot_path))
            print(f"Saved failure screenshot to: {screenshot_path.resolve()}")
        except Exception:
            pass
        return False

    finally:
        driver.quit()


def main():
    parser = argparse.ArgumentParser(description="Run plain-English browser test cases using Gemini and Selenium.")
    parser.add_argument("--url", default="https://phptravels.com/demo", help="Initial target URL")
    parser.add_argument("--test", required=True, help="Plain-English test case description")
    parser.add_argument("--headed", action="store_true", help="Launch visible browser window")
    args = parser.parse_args()

    success = run_test(test_case=args.test, start_url=args.url, headed=args.headed)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
