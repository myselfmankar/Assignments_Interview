using OpenQA.Selenium;

namespace AdaptiveFormAutomation.Core;

public interface IFieldInteractor
{
    bool Fill(IWebDriver driver, string contextDescription, IWebElement? container = null);
}
