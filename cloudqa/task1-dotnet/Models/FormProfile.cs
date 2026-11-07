namespace AdaptiveFormAutomation.Models;

public enum Gender
{
    Male,
    Female,
    Transgender,
    Other
}

public class FormProfile
{
    public string FirstName { get; set; } = "Vaishnav";
    public string LastName { get; set; } = "Mankar";
    public Gender Gender { get; set; } = Gender.Male;
    public string State { get; set; } = "India";
    public string DateOfBirth { get; set; } = "1998-05-15";
    public string Mobile { get; set; } = "9876543210";
    public string Email { get; set; } = "vaishnav@example.com";
    public string Country { get; set; } = "India";
    public string About { get; set; } = "Resilient automated test execution covering all DOM and Shadow DOM variants.";
    public bool AgreeTerms { get; set; } = true;

    public FormProfile() { }

    public FormProfile(string firstName, Gender gender, string state)
    {
        FirstName = firstName;
        Gender = gender;
        State = state;
    }

    public static FormProfile FromEnvironment()
    {
        var firstName = Environment.GetEnvironmentVariable("FIRST_NAME") ?? "Vaishnav";
        var state = Environment.GetEnvironmentVariable("STATE") ?? "India";

        var genderStr = Environment.GetEnvironmentVariable("GENDER") ?? "Male";
        if (!Enum.TryParse<Gender>(genderStr, true, out var gender))
        {
            gender = Gender.Male;
        }

        var profile = new FormProfile(firstName, gender, state)
        {
            LastName = Environment.GetEnvironmentVariable("LAST_NAME") ?? "Mankar",
            Mobile = Environment.GetEnvironmentVariable("MOBILE") ?? "9876543210",
            Email = Environment.GetEnvironmentVariable("EMAIL") ?? "vaishnav@example.com"
        };
        return profile;
    }

    public override string ToString() => $"[Profile: FirstName='{FirstName}', LastName='{LastName}', Gender={Gender}, State='{State}']";
}
