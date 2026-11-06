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
    public Gender Gender { get; set; } = Gender.Male;
    public string State { get; set; } = "India";

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

        return new FormProfile(firstName, gender, state);
    }

    public override string ToString() => $"[Profile: FirstName='{FirstName}', Gender={Gender}, State='{State}']";
}
