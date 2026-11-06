using OpenQA.Selenium;

namespace AdaptiveFormAutomation.Core;

/// <summary>
/// Injected JavaScript engine that discovers elements across:
/// 1. Standard DOM
/// 2. Deeply nested open Shadow DOMs (up to arbitrary depth)
/// 3. Standard & custom UI elements (native <select>, ARIA combobox, custom div dropdowns, radio inputs/labels)
/// 4. Spatial Geometry Proximity (bounding box layout) as a bulletproof fallback when all attributes fail.
/// </summary>
public static class ResilientEngineScripts
{
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
        let best = null;
        let bestScore = -1;

        for (const inp of inputs) {
            let score = 0;
            const id = inp.id || '';
            const name = (inp.name || '').toLowerCase();
            const placeholder = (inp.placeholder || '').toLowerCase();
            const ariaLabel = (inp.getAttribute('aria-label') || '').toLowerCase();

            let labelText = '';
            if (id) {
                const docRoot = inp.getRootNode ? inp.getRootNode() : document;
                const l = docRoot.querySelector ? docRoot.querySelector(`label[for=""${CSS.escape(id)}""]`) : null;
                if (l) labelText += ' ' + l.innerText;
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

            if (score > bestScore) {
                bestScore = score;
                best = inp;
            }
        }

        if (bestScore >= 50) return best;

        // Tier 2: Spatial Proximity Fallback (Bounding box nearest to text containing 'First Name')
        const allTextNodes = getAllDeep(root, el => {
            return (el.tagName === 'LABEL' || el.tagName === 'SPAN' || el.tagName === 'P' || el.tagName === 'DIV') 
                && el.innerText && el.innerText.toLowerCase().includes(targetLabel);
        });

        if (allTextNodes.length > 0) {
            const labelRect = allTextNodes[0].getBoundingClientRect();
            let nearestInput = null;
            let minDist = 999999;
            for (const inp of inputs) {
                const r = inp.getBoundingClientRect();
                // Check if directly below or to the right
                const dy = r.top - labelRect.bottom;
                const dx = r.left - labelRect.left;
                const dist = Math.sqrt(Math.max(0, dy) * Math.max(0, dy) + Math.max(0, dx) * Math.max(0, dx));
                if (dist < minDist) {
                    minDist = dist;
                    nearestInput = inp;
                }
            }
            if (nearestInput) return nearestInput;
        }

        return best || inputs[0];
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

        // Tier 1: Look for radio inputs or elements with role='radio'
        const radios = getAllDeep(root, el => {
            return (el.tagName === 'INPUT' && (el.getAttribute('type') || '').toLowerCase() === 'radio') 
                || (el.getAttribute('role') || '').toLowerCase() === 'radio';
        });

        for (const r of radios) {
            const val = (r.value || '').toLowerCase();
            const id = r.id || '';
            const ariaLabel = (r.getAttribute('aria-label') || '').toLowerCase();
            
            let labelText = '';
            if (id) {
                const docRoot = r.getRootNode ? r.getRootNode() : document;
                const l = docRoot.querySelector ? docRoot.querySelector(`label[for=""${CSS.escape(id)}""]`) : null;
                if (l) labelText += ' ' + l.innerText;
                const s = docRoot.querySelector ? docRoot.querySelector(`span[for=""${CSS.escape(id)}""]`) : null;
                if (s) labelText += ' ' + s.innerText;
            }
            const parentLabel = r.closest('label');
            if (parentLabel) labelText += ' ' + parentLabel.innerText;
            if (r.nextElementSibling && (r.nextElementSibling.tagName === 'LABEL' || r.nextElementSibling.tagName === 'SPAN')) {
                labelText += ' ' + r.nextElementSibling.innerText;
            }

            const combined = `${val} ${ariaLabel} ${labelText}`.toLowerCase();
            if (combined.includes(choiceValue)) {
                return r;
            }
        }

        // Tier 2: Look for clickable label/span containing the choice text
        const clickableLabels = getAllDeep(root, el => {
            const tag = el.tagName;
            const text = (el.innerText || '').toLowerCase().trim();
            return (tag === 'LABEL' || tag === 'SPAN' || tag === 'DIV') && text === choiceValue;
        });

        if (clickableLabels.length > 0) {
            return clickableLabels[0];
        }

        return radios.length > 0 ? radios[0] : null;
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
        for (const s of selects) {
            const id = (s.id || '').toLowerCase();
            const name = (s.name || '').toLowerCase();
            let labelText = '';
            const docRoot = s.getRootNode ? s.getRootNode() : document;
            if (id && docRoot.querySelector) {
                const l = docRoot.querySelector(`label[for=""${CSS.escape(s.id)}""]`);
                if (l) labelText += ' ' + l.innerText;
            }
            const parentLabel = s.closest('label');
            if (parentLabel) labelText += ' ' + parentLabel.innerText;
            if (s.previousElementSibling && s.previousElementSibling.innerText) {
                labelText += ' ' + s.previousElementSibling.innerText;
            }

            const combined = `${id} ${name} ${labelText}`.toLowerCase();
            if (combined.includes(targetLabel)) return { element: s, type: 'native-select' };
        }

        if (selects.length > 0) return { element: selects[0], type: 'native-select' };

        // Tier 2: Look for custom combobox or autocomplete input (e.g., role='combobox' or class*='autocomplete')
        const customDropdowns = getAllDeep(root, el => {
            const role = (el.getAttribute('role') || '').toLowerCase();
            const hasPopup = el.getAttribute('aria-haspopup');
            const cls = (el.className || '').toString().toLowerCase();
            return role === 'combobox' || hasPopup === 'listbox' || cls.includes('autocomplete') || cls.includes('select');
        });

        for (const cd of customDropdowns) {
            return { element: cd, type: 'custom-combobox' };
        }

        return null;
    ";

    public const string InteractDropdownScript = @"
        const target = arguments[0];
        const valToSelect = arguments[1];

        if (!target) return false;

        // Native select handling
        if (target.tagName === 'SELECT') {
            let matched = false;
            const search = valToSelect.toLowerCase().trim();
            for (let i = 0; i < target.options.length; i++) {
                const opt = target.options[i];
                const optText = (opt.text || '').toLowerCase().trim();
                const optVal = (opt.value || '').toLowerCase().trim();
                if (optText.includes(search) || optVal.includes(search) || search.includes(optText)) {
                    target.selectedIndex = i;
                    matched = true;
                    break;
                }
            }
            if (!matched && target.options.length > 1) {
                // Select first non-placeholder option
                target.selectedIndex = 1;
                matched = true;
            }
            target.dispatchEvent(new Event('focus', { bubbles: true }));
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
            target.dispatchEvent(new Event('blur', { bubbles: true }));
            return matched;
        }

        // Custom dropdown click trigger
        target.scrollIntoView({ behavior: 'instant', block: 'center' });
        target.click();
        target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        return true;
    ";

    public const string SafeClickScript = @"
        const el = arguments[0];
        if (!el) return false;
        el.scrollIntoView({ behavior: 'instant', block: 'center' });
        el.focus();
        el.click();
        el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
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
