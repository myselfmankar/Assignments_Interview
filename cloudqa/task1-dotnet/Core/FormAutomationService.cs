using OpenQA.Selenium;
using AdaptiveFormAutomation.Models;

namespace AdaptiveFormAutomation.Core;

public class FormAutomationService : IFormAutomationService
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
        Console.WriteLine("\n===============================================================================");
        Console.WriteLine("    ADAPTIVE FORM AUTOMATION (TIERED RESILIENCE ENGINE)");
        Console.WriteLine("===============================================================================");
        Console.WriteLine($"Configuration Profile: {_profile}");

        // Phase 1: Test Root Document & Open Shadow Roots
        _driver.SwitchTo().DefaultContent();
        ExecuteInCurrentContext("Root Document & Nested Shadow DOMs");

        // Phase 2: Recursively discover and test candidate IFrames that host form fields
        TraverseAndTestFrames(currentPath: "Top Window", depth: 1, maxDepth: 4);

        // Print Summary Table
        PrintSummary();
    }

    private void ExecuteInCurrentContext(string contextName)
    {
        var js = (IJavaScriptExecutor)_driver;
        var hasControls = (bool)(js.ExecuteScript(ResilientEngineScripts.HasFormControlsScript) ?? false);
        if (!hasControls)
        {
            // Context contains no form controls; skip gracefully without falsely marking it as a failed form
            return;
        }

        Console.WriteLine($"\n[Context] Testing: {contextName}");
        try
        {
            var firstNameInteractor = new FirstNameInteractor(_profile.FirstName);
            firstNameInteractor.Fill(_driver, contextName);
            Console.WriteLine($"  ✓ First Name verified: '{_profile.FirstName}'");

            var genderInteractor = new GenderInteractor(_profile.Gender);
            genderInteractor.Fill(_driver, contextName);
            Console.WriteLine($"  ✓ Gender verified: '{_profile.Gender}'");

            var stateInteractor = new StateInteractor(_profile.State);
            stateInteractor.Fill(_driver, contextName);
            Console.WriteLine($"  ✓ State verified: '{_profile.State}'");

            _results.Add(new ContextResult(contextName, true, _profile.FirstName, _profile.Gender.ToString(), _profile.State, null));
        }
        catch (Exception ex)
        {
            Console.WriteLine($"  ✗ Failed in context '{contextName}': {ex.Message}");
            _results.Add(new ContextResult(contextName, false, null, null, null, ex.Message));
        }
    }

    private void TraverseAndTestFrames(string currentPath, int depth, int maxDepth)
    {
        if (depth > maxDepth) return;

        var frameCount = _driver.FindElements(By.TagName("iframe")).Count;
        for (int i = 0; i < frameCount; i++)
        {
            try
            {
                var frames = _driver.FindElements(By.TagName("iframe"));
                if (i >= frames.Count) break;

                var frame = frames[i];
                var frameId = frame.GetDomAttribute("id") ?? "";
                var frameSrc = frame.GetDomAttribute("src") ?? "";
                var frameName = !string.IsNullOrEmpty(frameId) ? $"id='{frameId}'" : (!string.IsNullOrEmpty(frameSrc) ? $"src='{frameSrc}'" : $"index={i}");
                var subPath = $"{currentPath} -> Frame ({frameName})";

                _driver.SwitchTo().Frame(frame);
                ExecuteInCurrentContext(subPath);

                // Recurse into nested frames
                TraverseAndTestFrames(subPath, depth + 1, maxDepth);

                _driver.SwitchTo().ParentFrame();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  Notice on frame navigation ({currentPath} #{i}): {ex.Message}");
                _driver.SwitchTo().ParentFrame();
            }
        }
    }

    private void PrintSummary()
    {
        Console.WriteLine("\n===============================================================================");
        Console.WriteLine("                         EXECUTION RESULTS SUMMARY");
        Console.WriteLine("===============================================================================");
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

        Console.WriteLine("-------------------------------------------------------------------------------");
        Console.WriteLine($"Form Contexts Identified: {total} | Passed: {passed} | Failed: {total - passed}");
        Console.WriteLine("===============================================================================\n");

        if (passed == 0)
        {
            throw new Exception("Automation failed: No form context could be successfully completed.");
        }
    }
}
