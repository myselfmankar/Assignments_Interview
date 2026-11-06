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

        // Phase 1: Test Root Form & Open Shadow DOMs
        ExecuteInCurrentContext("Root Document & Nested Shadow DOMs");

        // Phase 2: Discover and Test all IFrames (with or without ID, including nested)
        TestAllFrames();

        // Print Summary Table
        PrintSummary();
    }

    private void ExecuteInCurrentContext(string contextName)
    {
        Console.WriteLine($"\n[Context] Testing: {contextName}");
        try
        {
            var firstNameInteractor = new FirstNameInteractor(_profile.FirstName);
            firstNameInteractor.Fill(_driver, contextName);
            Console.WriteLine($"  ✓ First Name filled: '{_profile.FirstName}'");

            var genderInteractor = new GenderInteractor(_profile.Gender);
            genderInteractor.Fill(_driver, contextName);
            Console.WriteLine($"  ✓ Gender selected: '{_profile.Gender}'");

            var stateInteractor = new StateInteractor(_profile.State);
            stateInteractor.Fill(_driver, contextName);
            Console.WriteLine($"  ✓ State selected: '{_profile.State}'");

            _results.Add(new ContextResult(contextName, true, _profile.FirstName, _profile.Gender.ToString(), _profile.State, null));
        }
        catch (Exception ex)
        {
            Console.WriteLine($"  ✗ Failed in context '{contextName}': {ex.Message}");
            _results.Add(new ContextResult(contextName, false, null, null, null, ex.Message));
        }
    }

    private void TestAllFrames()
    {
        _driver.SwitchTo().DefaultContent();
        var iframes = _driver.FindElements(By.TagName("iframe"));
        Console.WriteLine($"\nDiscovered {iframes.Count} top-level <iframe> elements.");

        for (int i = 0; i < iframes.Count; i++)
        {
            try
            {
                _driver.SwitchTo().DefaultContent();
                var currentFrame = _driver.FindElements(By.TagName("iframe"))[i];
                var frameId = currentFrame.GetDomAttribute("id") ?? "";
                var frameSrc = currentFrame.GetDomAttribute("src") ?? "";
                var frameDesc = $"IFrame #{i + 1} (id='{frameId}', src='{frameSrc}')";

                _driver.SwitchTo().Frame(currentFrame);
                ExecuteInCurrentContext(frameDesc);

                // Check for inner nested frames inside this iframe
                var innerFrames = _driver.FindElements(By.TagName("iframe"));
                for (int j = 0; j < innerFrames.Count; j++)
                {
                    try
                    {
                        var inner = _driver.FindElements(By.TagName("iframe"))[j];
                        var innerDesc = $"{frameDesc} -> Nested Frame #{j + 1}";
                        _driver.SwitchTo().Frame(inner);
                        ExecuteInCurrentContext(innerDesc);
                        _driver.SwitchTo().ParentFrame();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"  Notice: inner frame interaction note: {ex.Message}");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  Notice: skipping frame {i}: {ex.Message}");
            }
            finally
            {
                _driver.SwitchTo().DefaultContent();
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
        Console.WriteLine($"Total Contexts Evaluated: {total} | Passed: {passed} | Failed: {total - passed}");
        Console.WriteLine("===============================================================================\n");

        if (passed == 0)
        {
            throw new Exception("Automation failed: No form context could be successfully completed.");
        }
    }
}
