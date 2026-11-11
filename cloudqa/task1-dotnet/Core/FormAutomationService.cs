using OpenQA.Selenium;
using AdaptiveFormAutomation.Models;

namespace AdaptiveFormAutomation.Core;

public class FormAutomationService
{
    private readonly IWebDriver _driver;
    private readonly FormProfile _profile;
    private readonly List<ContextResult> _results = new();

    public FormAutomationService(IWebDriver driver, FormProfile profile)
    {
        _driver = driver;
        _profile = profile;
    }

    public void Execute()
    {
        Console.WriteLine("    ADAPTIVE FORM AUTOMATION (TIERED RESILIENCE ENGINE)");
        Console.WriteLine($"Configuration Profile: {_profile}\n");

        // Phase 1: Test Root Document & Shadow DOM Form Sections
        _driver.SwitchTo().DefaultContent();
        TestAllFormsInContext("Root Window");

        // Phase 2: Recursively discover and test candidate IFrames (with ID, without ID, and inside Shadow DOM)
        TraverseAndTestFrames(currentPath: "Root Window", depth: 1, maxDepth: 2);

        // Print Summary Table
        PrintSummary();
    }

    private void TestAllFormsInContext(string contextPath)
    {
        var js = (IJavaScriptExecutor)_driver;
        var hasControls = (bool)(js.ExecuteScript(ResilientEngineScripts.HasFormControlsScript) ?? false);
        if (!hasControls)
        {
            return;
        }

        var rawContainers = js.ExecuteScript(ResilientEngineScripts.FindFormContainersScript);
        if (rawContainers is not System.Collections.IEnumerable containerList)
        {
            ExecuteForm($"{contextPath} -> Default Context", null);
            return;
        }

        int count = 0;
        foreach (var item in containerList)
        {
            if (item is not Dictionary<string, object> dict) continue;

            var formName = dict.TryGetValue("name", out var nameObj) ? nameObj?.ToString() ?? "Form" : "Form";
            var formElement = dict.TryGetValue("element", out var elObj) ? elObj as IWebElement : null;
            var fullContextName = $"{contextPath} -> {formName}";

            ExecuteForm(fullContextName, formElement);
            count++;
        }

        if (count == 0)
        {
            ExecuteForm($"{contextPath} -> Default Context", null);
        }
    }

    private void ExecuteForm(string fullContextName, IWebElement? container)
    {
        Console.WriteLine($"\n[Context] Testing: {fullContextName}");
        try
        {
            // Core Required Field 1: First Name
            var firstNameInteractor = new FirstNameInteractor(_profile.FirstName);
            firstNameInteractor.Fill(_driver, fullContextName, container);
            Console.WriteLine($"  ✓ First Name verified: '{_profile.FirstName}'");

            // Core Required Field 2: Gender
            var genderInteractor = new GenderInteractor(_profile.Gender);
            genderInteractor.Fill(_driver, fullContextName, container);
            Console.WriteLine($"  ✓ Gender verified: '{_profile.Gender}'");

            // Core Required Field 3: State
            var stateInteractor = new StateInteractor(_profile.State);
            stateInteractor.Fill(_driver, fullContextName, container);
            Console.WriteLine($"  ✓ State verified: '{_profile.State}'");

            // Resilient Additional Field Population (Last Name, DOB, Mobile, Email, Country, Hobbies, About, Agreement)
            var js = (IJavaScriptExecutor)_driver;
            var payload = new Dictionary<string, object>
            {
                ["lastName"] = _profile.LastName,
                ["dob"] = _profile.DateOfBirth,
                ["mobile"] = _profile.Mobile,
                ["email"] = _profile.Email,
                ["country"] = _profile.Country,
                ["about"] = _profile.About
            };
            js.ExecuteScript(ResilientEngineScripts.FillAllAvailableFormFieldsScript, container, payload);
            Console.WriteLine("  ✓ Additional fields populated (Last Name, DOB, Mobile, Email, Country, Hobbies, About, Agreement)");

            _results.Add(new ContextResult(fullContextName, true, _profile.FirstName, _profile.Gender.ToString(), _profile.State, null));
        }
        catch (Exception ex)
        {
            Console.WriteLine($"  ✗ Failed in context '{fullContextName}': {ex.Message}");
            _results.Add(new ContextResult(fullContextName, false, null, null, null, ex.Message));
        }
    }

    private void TraverseAndTestFrames(string currentPath, int depth, int maxDepth)
    {
        if (depth > maxDepth) return;

        var js = (IJavaScriptExecutor)_driver;
        var rawFrames = js.ExecuteScript(ResilientEngineScripts.FindDeepIframesScript) as System.Collections.IEnumerable;
        if (rawFrames == null) return;

        var frameList = rawFrames.Cast<IWebElement>().ToList();
        for (int i = 0; i < frameList.Count; i++)
        {
            try
            {
                var refreshedFrames = (js.ExecuteScript(ResilientEngineScripts.FindDeepIframesScript) as System.Collections.IEnumerable)?.Cast<IWebElement>().ToList();
                if (refreshedFrames == null || i >= refreshedFrames.Count) break;

                var frame = refreshedFrames[i];
                var frameId = frame.GetDomAttribute("id") ?? "";
                var frameSrc = frame.GetDomAttribute("src") ?? "";

                // Check whether this iframe is inside a shadow DOM
                var isInShadow = (bool)(js.ExecuteScript("return arguments[0].getRootNode() !== document;", frame) ?? false);

                string friendlyFrameName;
                if (isInShadow)
                {
                    friendlyFrameName = "Section 'IFrame inside Shadow DOM'";
                }
                else if (string.IsNullOrEmpty(frameId))
                {
                    friendlyFrameName = "Section 'IFrame without ID'";
                }
                else
                {
                    friendlyFrameName = $"Section 'IFrame with ID' (id='{frameId}')";
                }

                // If this is an iframe embedding the full parent practice form, test its top level but do not recurse deeper to avoid infinite loop
                bool isSelfEmbedding = frameSrc.Contains("AutomationPracticeForm", StringComparison.OrdinalIgnoreCase);

                var subPath = $"{currentPath} -> {friendlyFrameName}";

                _driver.SwitchTo().Frame(frame);

                try
                {
                    TestAllFormsInContext(subPath);

                    if (!isSelfEmbedding && depth < maxDepth)
                    {
                        TraverseAndTestFrames(subPath, depth + 1, maxDepth);
                    }
                }
                finally
                {
                    _driver.SwitchTo().ParentFrame();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  Notice on frame navigation ({currentPath} #{i}): {ex.Message}");
                try { _driver.SwitchTo().ParentFrame(); } catch { }
            }
        }
    }

    private void PrintSummary()
    {
        Console.WriteLine("\n  EXECUTION RESULTS SUMMARY");
        
        int passed = _results.Count(r => r.Success);
        int total = _results.Count;

        foreach (var r in _results)
        {
            var status = r.Success ? "PASS [✓]" : "FAIL [✗]";
            Console.WriteLine($"{status} | {r.ContextName}");
            if (!r.Success && !string.IsNullOrEmpty(r.ErrorMessage))
            {
                Console.WriteLine($"       Reason: {r.ErrorMessage}");
            }
        }
        
        Console.WriteLine($"\nForm Contexts Identified: {total} | Passed: {passed} | Failed: {total - passed}");

        if (passed == 0)
        {
            throw new Exception("Automation failed: No form context could be successfully completed.");
        }
    }
}
