"""Simple test runner using creds dict formatted into the prompt via f-string."""
import subprocess
import sys

# 1. Simple credentials dictionary
CREDS = {
    "email": "vaishnavmankar.pict@gmail.com",
    "password": "AliceBay#123",
    "meet_title": "Onboarding Call",
    "meet_date": "10",
    "meet_platform": "Google Meet",
}

# 2. Plain-English test prompt formatted with f-string starting from https://phptravels.com/demo
TEST_PROMPT = (
    f"Navigate to the customer login or sign-in page from the demo page. "
    f"Log in as customer using email {CREDS['email']} and password {CREDS['password']}, "
    f"and click Sign In. Once on the dashboard, navigate to Meetings, click Create Meeting. "
    f"Fill Title with {CREDS['meet_title']}, click Start, click {CREDS['meet_date']}, click OK, "
    f"fill Location with {CREDS['meet_platform']}, and click Submit for Review. "
    f"Verify that Meeting request submitted for review is displayed."
)

URL = "https://phptravels.com/demo"

def main():
    print("=" * 70)
    print("Starting Test via Agent...")
    print(f"URL   : {URL}")
    print(f"Prompt: {TEST_PROMPT}")
    print("=" * 70)

    cmd = [
        sys.executable,
        "agent.py",
        "--url", URL,
        "--test", TEST_PROMPT,
        "--headed",
        "--keep-open",
    ]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
