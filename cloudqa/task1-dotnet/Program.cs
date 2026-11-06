using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Support.UI;
using OpenQA.Selenium;
using AdaptiveFormAutomation.Models;
using AdaptiveFormAutomation.Core;

// 1. Load Configuration & Data Model
var url = Environment.GetEnvironmentVariable("TARGET_URL") ?? "https://app.cloudqa.io/home/AutomationPracticeForm";
var profile = FormProfile.FromEnvironment();

Console.WriteLine($"Starting Resilient Automation on: {url}");

// 2. Setup Chrome Driver
var options = new ChromeOptions();
if (Environment.GetEnvironmentVariable("HEADLESS") != "0")
{
    options.AddArgument("--headless=new");
}
options.AddArgument("--no-sandbox");
options.AddArgument("--disable-dev-shm-usage");
options.AddArgument("--disable-gpu");
options.AddArgument("--window-size=1920,1080");

using var driver = new ChromeDriver(options);
driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(2);

try
{
    // 3. Navigate & Wait for Readystate
    driver.Navigate().GoToUrl(url);
    new WebDriverWait(driver, TimeSpan.FromSeconds(20))
        .Until(d => ((IJavaScriptExecutor)d).ExecuteScript("return document.readyState")?.ToString() == "complete");

    // 4. Execute Service
    var service = new FormAutomationService(driver, profile);
    service.Execute();
}
catch (Exception ex)
{
    Console.ForegroundColor = ConsoleColor.Red;
    Console.WriteLine($"FATAL: Automation run encountered an error: {ex.Message}");
    Console.ResetColor();
    Environment.Exit(1);
}
finally
{
    driver.Quit();
}
