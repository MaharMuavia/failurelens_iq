import sys
import os
import asyncio
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
# Load environment
load_dotenv()

from backend.services.foundry_openai_client import FoundryOpenAIClient

async def main():
    base_url = os.getenv("FOUNDRY_OPENAI_BASE_URL", "")
    api_key = os.getenv("FOUNDRY_API_KEY", "")
    deployment = os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "")

    if not base_url or not api_key or not deployment:
        print("Error: FOUNDRY_OPENAI_BASE_URL, FOUNDRY_API_KEY, and FOUNDRY_MODEL_DEPLOYMENT must be set in your .env file.")
        sys.exit(1)

    print("Initializing FoundryOpenAIClient...")
    print(f"Base URL: {base_url}")
    print(f"Deployment: {deployment}")
    print("API Key: [HIDDEN]")

    client = FoundryOpenAIClient(
        base_url=base_url,
        api_key=api_key,
        deployment=deployment
    )

    print("\nSending completion request: 'Say OK from FailureLens IQ'...")
    try:
        response = await client.chat_completion_raw(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say OK from FailureLens IQ"
        )
        if response["ok"]:
            print("\nRequest Successful!")
            print(f"Provider: {response['provider']}")
            print(f"Model: {response['model']}")
            print(f"Response: {response['content'].strip()}")
        else:
            print("\nRequest Failed!")
            print(f"Detail: {response.get('detail')}")
            sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during completion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
