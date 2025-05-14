# pegasus_llm.py
from huggingface_hub import InferenceClient
from tenacity import retry, wait_incrementing, stop_after_attempt

class PegasusLLM:
    def __init__(self, api_key: str, model: str = "huggingface/pegasus-xsum"):
        # Initialize the InferenceClient with your API token.
        self.client = InferenceClient(token=api_key)
        self.model = model

    # Retry logic: Incrementally wait starting at 60 seconds, increasing by 60 seconds up to 3600 seconds,
    # and stop after 5000 attempts.
    @retry(wait=wait_incrementing(start=60, increment=60, max=3600), stop=stop_after_attempt(5000))
    def invoke(self, prompt: str):
        # Call the summarization endpoint by passing the prompt as a positional argument.
        result = self.client.summarization(prompt, model=self.model)
        # If the result contains an error message, trigger a retry.
        if "error" in str(result).lower():
            print("Error in response; retrying...")
            raise Exception("Error in Response")
        # Return an object with a .content attribute for compatibility.
        return type("LLMResponse", (object,), {"content": result})
