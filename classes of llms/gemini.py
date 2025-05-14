from google import genai
from tenacity import retry, wait_exponential, stop_after_attempt,wait_fixed,wait_incrementing
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from dotenv import load_dotenv

import openai
import time
import os
class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = model

    # Apply retry logic with exponential backoff
    # @retry(wait=wait_exponential(multiplier=1, min=60, max=3600), stop=stop_after_attempt(5000))
    @retry(wait=wait_incrementing(start=60, increment=60, max=3600), stop=stop_after_attempt(5000))

    def invoke(self, prompt: str):
        response = self.client.models.generate_content(model=self.model, contents=prompt)

        # Check if the response contains an error message; if so, trigger a retry
        if "error" in response.text.lower():  # Check for the presence of "error" in the response text
            print("Error in Response")
            raise Exception("Error in Response")

        # Return an object with .content for compatibility
        return type("LLMResponse", (object,), {"content": response.text or ""})

class OpenRouterLLM:
    def __init__(self, api_key: str, model: str = "qwen/qwq-32b:free", base_url: str = "https://openrouter.ai/api/v1"):
        """
        Initialize the OpenRouterLLM client.

        Args:
            api_key (str): Your API key.
            model (str): The model identifier to use (default is Deepseek's free model).
            base_url (str): Base URL for the OpenRouter API.
        """
        openai.api_key = api_key
        openai.api_base = base_url
        self.model = model

    def invoke(self, prompt: str):
        """
        Sends the prompt to the model and returns the response.

        Args:
            prompt (str): The text prompt for the model.

        Returns:
            An object with a 'content' attribute containing the model's response.
        """
        response = openai.chat.completions.create( # Use openai.chat.completions.create instead of openai.ChatCompletion.create
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional: Replace with your site's URL if needed.
                "X-Title": "<YOUR_SITE_NAME>"        # Optional: Replace with your site's name if needed.
            }
        )
        # Wrap the response in an object with a .content attribute for compatibility.
        return type("LLMResponse", (object,), {"content": response.choices[0].message.content})

gemini_llm = GeminiLLM(
        api_key=os.getenv("GOOGLE_API_KEY"),  # <-- Replace with your actual key
        model="gemini-2.0-flash"
    )

prompt = "What is the capital of France?"
response = gemini_llm.invoke(prompt)
print(response.content)  # Should print the response from the model