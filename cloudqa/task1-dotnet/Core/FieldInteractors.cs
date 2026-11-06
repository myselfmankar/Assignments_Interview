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
            throw new NoSuchElementException($"Could not locate 'First Name' input field in {contextDescription}");
        }

        try
        {
            element.Clear();
            element.SendKeys(_name);
        }
        catch
        {
            js.ExecuteScript(ResilientEngineScripts.SetValueScript, element, _name);
        }

        // Verification: ensure the field actually contains the value
        var verified = (bool)(js.ExecuteScript(ResilientEngineScripts.VerifyInputValueScript, element, _name) ?? false);
        if (!verified)
        {
            throw new InvalidOperationException($"Verification failed: 'First Name' does not contain '{_name}'");
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
            throw new NoSuchElementException($"Could not locate 'Gender' option '{choiceString}' in {contextDescription}");
        }

        try
        {
            element.Click();
        }
        catch
        {
            js.ExecuteScript(ResilientEngineScripts.SafeClickScript, element);
        }

        // Verification: check if the radio was successfully checked
        var isChecked = (bool)(js.ExecuteScript(ResilientEngineScripts.VerifyRadioSelectedScript, element) ?? false);
        if (!isChecked)
        {
            throw new InvalidOperationException($"Verification failed: Gender radio option '{choiceString}' is not selected.");
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
            var interactRes = js.ExecuteScript(ResilientEngineScripts.InteractDropdownScript, el, _state);
            if (interactRes is not Dictionary<string, object> resDict)
            {
                throw new InvalidOperationException(
                    $"State selection returned an unexpected result type in {contextDescription}.");
            }

            var success = resDict.TryGetValue("success", out var successValue)
                && successValue is bool selected
                && selected;

            if (!success)
            {
                var reason = resDict.TryGetValue("reason", out var reasonValue)
                    ? reasonValue?.ToString()
                    : "No verification result was returned.";
                throw new InvalidOperationException($"Failed to select State '{_state}': {reason}");
            }

            return true;
        }

        throw new NoSuchElementException($"Could not locate 'State' dropdown in {contextDescription}");
    }
}
