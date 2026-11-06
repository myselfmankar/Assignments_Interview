using OpenQA.Selenium;

namespace AdaptiveFormAutomation.Core;

/// <summary>
/// Injected JavaScript engine that discovers elements across:
/// 1. Standard DOM
/// 2. Deeply nested open Shadow DOMs (up to arbitrary depth)
/// 3. Standard & custom UI elements
/// 4. Spatial Geometry Proximity fallback with strict threshold and ambiguity checks.
/// </summary>
public static class ResilientEngineScripts
{
    // Script to check if the current context contains form controls
    public const string HasFormControlsScript = @"
        const root = document;
        function hasInputs(node) {
            if (!node) return false;
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (['INPUT', 'SELECT', 'TEXTAREA'].includes(node.tagName)) return true;
                if (node.shadowRoot && hasInputs(node.shadowRoot)) return true;
            }
            const children = node.children || [];
            for (let i = 0; i < children.length; i++) {
                if (hasInputs(children[i])) return true;
            }
            return false;
        }
        return hasInputs(root);
    ";

    public const string FindTextInputScript = @"
        const targetLabel = (arguments[0] || '').toLowerCase().trim();
        const root = arguments[1] || document;

        function getAllDeep(node, filterFn) {
            let res = [];
            if (!node) return res;
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (filterFn(node)) res.push(node);
                if (node.shadowRoot) {
                    res.push(...getAllDeep(node.shadowRoot, filterFn));
                }
            }
            const children = node.children || [];
            for (let i = 0; i < children.length; i++) {
                res.push(...getAllDeep(children[i], filterFn));
            }
            return res;
        }

        const isTextInput = el => {
            if (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA') return false;
            const type = (el.getAttribute('type') || 'text').toLowerCase();
            return ['text', 'search', 'email', 'tel', 'url', ''].includes(type);
        };

        const inputs = getAllDeep(root, isTextInput);
        if (inputs.length === 0) return null;

        // Tier 1: Computed label / accessibility name / explicit <label for>
        let scored = [];

        for (const inp of inputs) {
            let score = 0;
            const id = inp.id || '';
            const name = (inp.name || '').toLowerCase();
            const placeholder = (inp.placeholder || '').toLowerCase();
            const ariaLabel = (inp.getAttribute('aria-label') || '').toLowerCase();

            let labelText = '';
            if (id) {
                const docRoot = inp.getRootNode ? inp.getRootNode() : document;
                if (docRoot.querySelector) {
                    try {
                        const l = docRoot.querySelector('label[for=""' + CSS.escape(id) + '""]');
                        if (l) labelText += ' ' + l.innerText;
                    } catch (e) {}
                }
            }
            const parentLabel = inp.closest('label');
            if (parentLabel) labelText += ' ' + parentLabel.innerText;
            if (inp.labels && inp.labels.length) {
                for (let j = 0; j < inp.labels.length; j++) labelText += ' ' + inp.labels[j].innerText;
            }

            const combined = `${labelText} ${name} ${placeholder} ${ariaLabel}`.toLowerCase();

            if (combined.includes(targetLabel)) score += 100;
            if (targetLabel.includes('first') && combined.includes('first')) score += 50;
            if (combined.includes('name') && !combined.includes('last')) score += 20;
            if (combined.includes('last') && targetLabel.includes('first')) score -= 80;

            if (score >= 40) {
                scored.push({ input: inp, score });
            }
        }

        scored.sort((a, b) => b.score - a.score);

        // Reject if ambiguous
        if (scored.length > 1 && scored[0].score === scored[1].score && scored[0].score >= 50) {
            // Check if one is an exact match for targetLabel
            const exact0 = scored[0].input.placeholder?.toLowerCase() === targetLabel || scored[0].input.name?.toLowerCase() === targetLabel;
            const exact1 = scored[1].input.placeholder?.toLowerCase() === targetLabel || scored[1].input.name?.toLowerCase() === targetLabel;
            if (exact0 && !exact1) return scored[0].input;
            if (!exact0 && exact1) return scored[1].input;
        }

        if (scored.length > 0 && scored[0].score >= 40) {
            return scored[0].input;
        }

        // Tier 2: Spatial Proximity Fallback with confidence threshold
        const allTextNodes = getAllDeep(root, el => {
            return (el.tagName === 'LABEL' || el.tagName === 'SPAN' || el.tagName === 'P' || el.tagName === 'DIV') 
                && el.innerText && el.innerText.toLowerCase().trim().includes(targetLabel);
        });

        if (allTextNodes.length > 0) {
            const labelRect = allTextNodes[0].getBoundingClientRect();
            let nearestInput = null;
            let minDist = 300; // Must be within reasonable pixel proximity
            for (const inp of inputs) {
                const r = inp.getBoundingClientRect();
                const dy = r.top - labelRect.bottom;
                const dx = r.left - labelRect.left;
                if (dy >= -20 && dy <= 120 && Math.abs(dx) <= 300) {
                    const dist = Math.sqrt(Math.max(0, dy) * Math.max(0, dy) + Math.max(0, dx) * Math.max(0, dx));
                    if (dist < minDist) {
                        minDist = dist;
                        nearestInput = inp;
                    }
                }
            }
            if (nearestInput) return nearestInput;
        }

        // Return null instead of unsafe inputs[0]
        return null;
    ";

    public const string FindRadioChoiceScript = @"
        const groupLabel = (arguments[0] || '').toLowerCase().trim();
        const choiceValue = (arguments[1] || '').toLowerCase().trim();
        const root = arguments[2] || document;

        function getAllDeep(node, filterFn) {
            let res = [];
            if (!node) return res;
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (filterFn(node)) res.push(node);
                if (node.shadowRoot) {
                    res.push(...getAllDeep(node.shadowRoot, filterFn));
                }
            }
            const children = node.children || [];
            for (let i = 0; i < children.length; i++) {
                res.push(...getAllDeep(children[i], filterFn));
            }
            return res;
        }

        const radios = getAllDeep(root, el => {
            return (el.tagName === 'INPUT' && (el.getAttribute('type') || '').toLowerCase() === 'radio') 
                || (el.getAttribute('role') || '').toLowerCase() === 'radio';
        });

        // 1. Group-Constrained matching: Must match group label AND choice value
        let matches = [];
        for (const r of radios) {
            const val = (r.value || '').toLowerCase();
            const name = (r.name || '').toLowerCase();
            const id = r.id || '';
            const ariaLabel = (r.getAttribute('aria-label') || '').toLowerCase();
            
            let labelText = '';
            if (id) {
                const docRoot = r.getRootNode ? r.getRootNode() : document;
                if (docRoot.querySelector) {
                    try {
                        const l = docRoot.querySelector('label[for=""' + CSS.escape(id) + '""]');
                        if (l) labelText += ' ' + l.innerText;
                        const s = docRoot.querySelector('span[for=""' + CSS.escape(id) + '""]');
                        if (s) labelText += ' ' + s.innerText;
                    } catch (e) {}
                }
            }
            const parentLabel = r.closest('label');
            if (parentLabel) labelText += ' ' + parentLabel.innerText;
            if (r.nextElementSibling && (r.nextElementSibling.tagName === 'LABEL' || r.nextElementSibling.tagName === 'SPAN')) {
                labelText += ' ' + r.nextElementSibling.innerText;
            }

            // Check group context (parent container text or radio name)
            const groupText = ((r.closest('.form-group, fieldset, div')?.innerText || '') + ' ' + name).toLowerCase();
            const inGenderGroup = groupText.includes(groupLabel);

            const combinedVal = `${val} ${ariaLabel} ${labelText}`.toLowerCase();
            if (combinedVal.includes(choiceValue)) {
                matches.push({ radio: r, inGroup: inGenderGroup });
            }
        }

        // Only accept a unique match in the labelled group. If the group cannot
        // be established, accept a globally unique option; otherwise fail closed.
        const groupMatches = matches.filter(m => m.inGroup);
        if (groupMatches.length === 1) return groupMatches[0].radio;
        if (groupMatches.length > 1) return null;
        if (matches.length === 1) return matches[0].radio;
        return null;
    ";

    public const string FindDropdownScript = @"
        const targetLabel = (arguments[0] || '').toLowerCase().trim();
        const root = arguments[1] || document;

        function getAllDeep(node, filterFn) {
            let res = [];
            if (!node) return res;
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (filterFn(node)) res.push(node);
                if (node.shadowRoot) {
                    res.push(...getAllDeep(node.shadowRoot, filterFn));
                }
            }
            const children = node.children || [];
            for (let i = 0; i < children.length; i++) {
                res.push(...getAllDeep(children[i], filterFn));
            }
            return res;
        }

        // Tier 1: Look for native <select>
        const selects = getAllDeep(root, el => el.tagName === 'SELECT');
        let scored = [];
        for (const s of selects) {
            const id = (s.id || '').toLowerCase();
            const name = (s.name || '').toLowerCase();
            let labelText = '';
            const docRoot = s.getRootNode ? s.getRootNode() : document;
            if (id && docRoot.querySelector) {
                try {
                    const l = docRoot.querySelector('label[for=""' + CSS.escape(s.id) + '""]');
                    if (l) labelText += ' ' + l.innerText;
                } catch(e) {}
            }
            const parentLabel = s.closest('label');
            if (parentLabel) labelText += ' ' + parentLabel.innerText;
            if (s.previousElementSibling && s.previousElementSibling.innerText) {
                labelText += ' ' + s.previousElementSibling.innerText;
            }

            const combined = `${id} ${name} ${labelText}`.toLowerCase();
            if (combined.includes(targetLabel)) {
                scored.push({ element: s, type: 'native-select', score: 100 });
            }
        }

        if (scored.length > 0) return scored[0];
        if (selects.length === 1) return { element: selects[0], type: 'native-select', score: 50 };

        // Tier 2: Look for custom combobox
        const customDropdowns = getAllDeep(root, el => {
            const role = (el.getAttribute('role') || '').toLowerCase();
            const hasPopup = el.getAttribute('aria-haspopup');
            const cls = (el.className || '').toString().toLowerCase();
            return role === 'combobox' || hasPopup === 'listbox' || cls.includes('autocomplete') || cls.includes('select');
        });

        for (const cd of customDropdowns) {
            const parentText = (cd.closest('.form-group, div')?.innerText || '').toLowerCase();
            if (parentText.includes(targetLabel)) {
                return { element: cd, type: 'custom-combobox', score: 80 };
            }
        }

        return null;
    ";

    public const string InteractDropdownScript = @"
        const target = arguments[0];
        const valToSelect = arguments[1];

        if (!target) return { success: false, reason: 'Target element is null' };

        // Native select handling
        if (target.tagName === 'SELECT') {
            let matched = false;
            let matchedIndex = -1;
            const search = valToSelect.toLowerCase().trim();
            for (let i = 0; i < target.options.length; i++) {
                const opt = target.options[i];
                const optText = (opt.text || '').toLowerCase().trim();
                const optVal = (opt.value || '').toLowerCase().trim();
                if (optText === search || optVal === search || optText.includes(search) || optVal.includes(search)) {
                    target.selectedIndex = i;
                    matched = true;
                    matchedIndex = i;
                    break;
                }
            }

            if (!matched) {
                return { success: false, reason: `Requested option '${valToSelect}' not found in dropdown.` };
            }

            target.dispatchEvent(new Event('focus', { bubbles: true }));
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
            target.dispatchEvent(new Event('blur', { bubbles: true }));

            // Verification
            const finalIndex = target.selectedIndex;
            const selectedText = target.options[finalIndex]?.text || '';
            const selectedVal = target.options[finalIndex]?.value || '';
            const verified = selectedText.toLowerCase().includes(search) || selectedVal.toLowerCase().includes(search);
            return { success: verified, selectedValue: selectedText, reason: verified ? null : 'Selection verification mismatch' };
        }

        // Custom dropdown: open it, locate a visible option, select it, and
        // verify that the control reflects the requested value. A successful
        // click on the trigger alone is never considered a successful select.
        const search = (valToSelect || '').toLowerCase().trim();
        if (!search) return { success: false, reason: 'Requested option is empty.' };
        target.scrollIntoView({ behavior: 'instant', block: 'center' });
        target.click();

        function collectDeep(node, out = []) {
            if (!node) return out;
            if (node.nodeType === Node.ELEMENT_NODE) {
                out.push(node);
                if (node.shadowRoot) collectDeep(node.shadowRoot, out);
            }
            for (const child of (node.children || [])) collectDeep(child, out);
            return out;
        }
        const isVisible = el => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.display !== 'none' &&
                   s.visibility !== 'hidden' && s.opacity !== '0';
        };
        const candidates = collectDeep(document).filter(el => {
            const role = (el.getAttribute('role') || '').toLowerCase();
            return ['option', 'menuitem', 'listitem'].includes(role) ||
                   el.tagName === 'OPTION' ||
                   el.matches('[data-value], li');
        }).filter(isVisible);
        const scored = candidates.map(el => {
            const text = (el.innerText || el.textContent || '').trim().toLowerCase();
            const value = (el.getAttribute('data-value') || el.getAttribute('value') || '').trim().toLowerCase();
            return { el, score: text === search || value === search ? 100 :
                                (text.includes(search) || value.includes(search) ? 60 : 0) };
        }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);
        if (!scored.length || (scored.length > 1 && scored[0].score === scored[1].score)) {
            return { success: false, reason: 'Could not identify one unambiguous visible option: ' + valToSelect };
        }
        scored[0].el.click();

        const selectedText = (target.getAttribute('aria-valuetext') ||
                              target.getAttribute('value') ||
                              target.value ||
                              target.innerText ||
                              target.textContent || '').trim().toLowerCase();
        const selectedOption = target.getAttribute('aria-expanded') === 'false' &&
            (scored[0].el.getAttribute('aria-selected') === 'true' ||
             scored[0].el.getAttribute('aria-checked') === 'true');
        const verified = selectedText.includes(search) || selectedOption;
        return { success: verified, selectedValue: selectedText,
                 reason: verified ? null : 'Custom dropdown did not expose the requested selected value.' };
    ";

    public const string VerifyInputValueScript = @"
        const el = arguments[0];
        const expected = (arguments[1] || '').toLowerCase().trim();
        if (!el) return false;
        const actual = (el.value || '').toLowerCase().trim();
        return expected.length > 0 && actual === expected;
    ";

    public const string VerifyRadioSelectedScript = @"
        const el = arguments[0];
        if (!el) return false;
        if (el.matches && el.matches('input[type=""radio""]')) return el.checked === true;
        if ((el.getAttribute('role') || '').toLowerCase() === 'radio') {
            return el.getAttribute('aria-checked') === 'true';
        }
        const id = el.getAttribute('for');
        if (id) {
            const root = el.getRootNode ? el.getRootNode() : document;
            const input = root.getElementById ? root.getElementById(id) :
                (root.querySelector ? root.querySelector('#' + CSS.escape(id)) : null);
            if (input && input.matches('input[type=""radio""]')) return input.checked === true;
        }
        return false;
    ";

    public const string SafeClickScript = @"
        const el = arguments[0];
        if (!el) return false;
        el.scrollIntoView({ behavior: 'instant', block: 'center' });
        el.focus();
        el.click();
        return true;
    ";

    public const string SetValueScript = @"
        const el = arguments[0];
        const text = arguments[1];
        if (!el) return false;
        el.scrollIntoView({ behavior: 'instant', block: 'center' });
        el.focus();
        el.value = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        el.dispatchEvent(new Event('blur', { bubbles: true }));
        return true;
    ";
}
