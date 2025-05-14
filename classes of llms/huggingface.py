from huggingface_hub import InferenceClient
from tenacity import retry, wait_incrementing, stop_after_attempt
from dotenv import load_dotenv
import os

class DeepseekLLM:
    def __init__(self, api_key: str, model: str = "deepseek-ai/DeepSeek-R1"):
        # Initialize the Hugging Face InferenceClient with your API token.
        self.client = InferenceClient(token=api_key)
        self.model = model

    # Retry logic: Wait incrementally (starting at 60s, increasing by 60s, max 3600s) and stop after 5000 attempts.
    # @retry(wait=wait_incrementing(start=60, increment=60, max=3600), stop=stop_after_attempt(5000))
    def invoke(self, prompt: str):
        messages = [{"role": "user", "content": prompt}]
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=500,
        )
        # Optionally check for errors in the response.
        if "error" in str(completion).lower():
            print("Error in response; retrying...")
            raise Exception("Error in Response")
        # Wrap the result in an object with a .content attribute.
        return type("LLMResponse", (object,), {"content": completion.choices[0].message})

# Usage example:
api_key=os.getenv("HUGGING_FACE_API_KEY")  # Replace with your actual API key.
prompt = "What is the capital of France?"

deepseek_llm = DeepseekLLM(api_key=api_key)
response = deepseek_llm.invoke(prompt)
print(response.content)
