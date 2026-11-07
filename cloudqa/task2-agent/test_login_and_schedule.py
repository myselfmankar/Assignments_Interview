"""Demo runner for the customer meeting workflow.

Set CUSTOMER_EMAIL, CUSTOMER_PASSWORD and GEMINI_API_KEY in your environment.
Credentials are inserted into the validated plan locally, after Gemini responds,
so they are not sent to the model as part of the planning prompt.
"""
import os
import subprocess
import sys

URL = "https://phptravels.com/demo"

TEST_PROMPT = (
    "Navigate from the demo page to the customer sign-in page. "
    "Sign in using email {{CUSTOMER_EMAIL}} and password {{CUSTOMER_PASSWORD}}. "
    "After reaching the dashboard, open Meetings and choose Create Meeting. "
    "Create a meeting titled 'Onboarding Call', set the date to the 10th, "
    "set the location to 'Google Meet', and submit it for review. "
    "Verify that the meeting request confirmation is displayed."
)


def main() -> None:
    required = ("GEMINI_API_KEY", "CUSTOMER_EMAIL", "CUSTOMER_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise SystemExit("Missing required environment variables: " + ", ".join(missing))

    print("Starting customer meeting workflow (credentials hidden).")
    cmd = [
        sys.executable,
        "agent.py",
        "--url", URL,
        "--test", TEST_PROMPT,
        "--headed",
        "--keep-open",
    ]
    result = subprocess.run(cmd, check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
