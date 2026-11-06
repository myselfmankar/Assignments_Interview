namespace AdaptiveFormAutomation.Models;

public record ContextResult(
    string ContextName,
    bool Success,
    string? FirstNameDetails,
    string? GenderDetails,
    string? StateDetails,
    string? ErrorMessage
);
