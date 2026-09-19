import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# GEMINI CLIENT
# =========================================================

class GeminiClient:

    def __init__(self):

        if not GEMINI_API_KEY:

            raise ValueError(
                "GEMINI_API_KEY was not found. "
                "Please add GEMINI_API_KEY to the .env file."
            )


        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )


        self.model = GEMINI_MODEL


        print(
            "Gemini client initialized successfully."
        )

        print(
            f"Model: {self.model}"
        )


    # =====================================================
    # GENERATE RESPONSE
    # =====================================================

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:

        if not prompt.strip():

            raise ValueError(
                "Prompt cannot be empty."
            )


        print(
            "Sending request to Gemini..."
        )


        try:

            config = None


            if system_instruction:

                config = types.GenerateContentConfig(
                    system_instruction=system_instruction
                )


            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )


            print(
                "Gemini response received."
            )


        except Exception as error:

            error_text = str(error)


            print(
                "\nGEMINI API ERROR"
            )

            print(
                "-" * 60
            )

            print(
                error_text
            )

            print(
                "-" * 60
            )


            if (
                "429" in error_text
                or "rate limit"
                in error_text.lower()
                or "too many requests"
                in error_text.lower()
            ):

                raise RuntimeError(
                    "The Gemini API request limit "
                    "has been reached. Please try again "
                    "after the quota resets."
                ) from error


            raise RuntimeError(
                "The Gemini API request failed. "
                "Please check the Gemini API configuration "
                "and model name."
            ) from error


        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )


        return response.text.strip()


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GEMINI CONNECTION TEST")
    print("=" * 60)


    try:

        client = GeminiClient()


        result = client.generate(
            "Reply with exactly: GEMINI WORKS"
        )


        print()
        print("RESULT:")
        print(result)


        print()
        print("=" * 60)
        print("GEMINI CONNECTION SUCCESSFUL")
        print("=" * 60)


    except Exception as error:

        print()
        print("=" * 60)
        print("GEMINI CONNECTION FAILED")
        print("=" * 60)
        print(error)