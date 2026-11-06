using OpenQA.Selenium;
using AdaptiveFormAutomation.Models;

namespace AdaptiveFormAutomation.Core;

public class FirstNameInteractor : IFieldInteractor
{
    private readonly string _name;

    public FirstNameInteractor(string name)
    {
        _name = name;
    }

    public bool Fill(IWebDriver driver, string contextDescription)
    {
        var js = (IJavaScriptExecutor)driver;
        var element = js.ExecuteScript(ResilientEngineScripts.FindTextInputScript, "first name") as IWebElement;

        if (element == null)
        {
            throw new NoSuchElementException($"[Tier 1/2/3] Could not locate 'First Name' input field in {contextDescription}");
        }

        try
        {
            element.Clear();
            element.SendKeys(_name);
        }
        catch
        {
            // Fallback to JS event injection if intercepted or obscured
            js.ExecuteScript(ResilientEngineScripts.SetValueScript, element, _name);
        }

        return true;
    }
}

public class GenderInteractor : IFieldInteractor
{
    private readonly Gender _gender;

    public GenderInteractor(Gender gender)
    {
        _gender = gender;
    }

    public bool Fill(IWebDriver driver, string contextDescription)
    {
        var js = (IJavaScriptExecutor)driver;
        var choiceString = _gender.ToString();
        var element = js.ExecuteScript(ResilientEngineScripts.FindRadioChoiceScript, "gender", choiceString) as IWebElement;

        if (element == null)
        {
            throw new NoSuchElementException($"[Tier 1/2] Could not locate 'Gender' choice '{choiceString}' in {contextDescription}");
        }

        try
        {
            element.Click();
        }
        catch
        {
            // Fallback to synthetic JS click
            js.ExecuteScript(ResilientEngineScripts.SafeClickScript, element);
        }

        return true;
    }
}

public class StateInteractor : IFieldInteractor
{
    private readonly string _state;

    public StateInteractor(string state)
    {
        _state = state;
    }

    public bool Fill(IWebDriver driver, string contextDescription)
    {
        var js = (IJavaScriptExecutor)driver;
        var res = js.ExecuteScript(ResilientEngineScripts.FindDropdownScript, "state");

        if (res is Dictionary<string, object> dict && dict.TryGetValue("element", out var elObj) && elObj is IWebElement el)
        {
            var success = (bool)(js.ExecuteScript(ResilientEngineScripts.InteractDropdownScript, el, _state) ?? false);
            return success;
        }

        // Direct search fallback: any <select> in context
        var selects = driver.FindElements(By.TagName("select"));
        if (selects.Count > 0)
        {
            js.ExecuteScript(ResilientEngineScripts.InteractDropdownScript, selects[0], _state);
            return true;
        }

        throw new NoSuchElementException($"[Tier 1/2/3] Could not locate 'State' dropdown in {contextDescription}");
    }
}
