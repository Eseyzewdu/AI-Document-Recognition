import os
import time

try:
    from dotenv import load_dotenv
    from google import genai
    from google.genai import errors
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing project dependencies. Activate the project virtual environment or run: "
        "python -m pip install -r requirements.txt"
    ) from exc

# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: API key not found in .env file")
else:
    try:
        client = genai.Client(api_key=api_key)

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents="Explain artificial intelligence in 3 simple sentences."
                )
                break
            except errors.ServerError as exc:
                if exc.code != 503 or attempt == 2:
                    raise

                delay = 2 ** (attempt + 1)
                print(f"Gemini is busy; retrying in {delay} seconds...")
                time.sleep(delay)

        print("\nGEMINI CONNECTION SUCCESSFUL!")
        print(response.text)

    except Exception as e:
        print("Gemini connection failed:")
        print(e)
        if getattr(e, "code", None) == 503:
            print("Gemini is temporarily overloaded. Please try again later.")