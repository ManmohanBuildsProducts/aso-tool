#!/usr/bin/env python3
"""
<Installation>:
    pip install --upgrade anthropic
</Installation>

<Usage>:
    from dotenv import load_dotenv
    sys.path.append(str(Path(__file__).parent))
    from external_integrations.claude_client import query_claude_model
    
    load_dotenv(ROOT_DIR / '.env')

    response = query_claude_model(
        model="claude-3-7-sonnet-20250219",
        user_prompt="What is the capital of Germany?"
    )

    - Response: {'model': 'claude-3-7-sonnet-20250219', 'reply': 'The capital of Germany is Berlin. It has been the capital since German reunification in 1990, following the fall of the Berlin Wall in 1989.'}
    
    # Claude 3-7 with thinking enabled:
    response = query_claude_model(
        model="claude-3-7-sonnet-20250219",
        user_prompt="What is the capital of Germany?",
        thinking={"type": "enabled", "budget_tokens": 5000}
    )
</Usage>

<Supported_Models>:
    - claude-3-7-sonnet-20250219
    - claude-3-5-sonnet-20241022
    - claude-3-5-haiku-20241022
</Supported_Models>
"""
import os
import argparse
import anthropic

def query_claude_model(model: str, user_prompt: str, enable_thinking: bool = False) -> dict:
    """
    Query Anthropic Claude models.

    Args:
        model (str): Model name (e.g., claude-3-7-sonnet-20250219)
        user_prompt (str): Prompt/question to send to the model
        thinking (dict, optional): Configuration for model thinking.
                                  Example: {"type": "enabled", "budget_tokens": 5000}

    Returns:
        dict: Response containing model output and reply

    Raises:
        ValueError: If API key is missing or prompt is empty
    """
    # Validate environment
    if not (api_key := os.environ.get("ANTHROPIC_API_KEY")):
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    if not user_prompt.strip():
        raise ValueError("Empty prompt")

    # Initialize the Anthropic client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Create message parameters
    message_params = {
        "model": model,
        "max_tokens": 20000,
        "messages": [{
            "role": "user",
            "content": user_prompt
        }]
    }
    
    # Add thinking parameter if provided
    if enable_thinking:
        message_params["thinking"] = {
                                        "type": "enabled",
                                        "budget_tokens": 16000
                                    }
    
    response = client.messages.create(**message_params)
    
    try:
        if enable_thinking:
            reasoning = response.content[0].thinking
            reply = response.content[1].text
            output = {
                "reasoning": reasoning,
                "reply": reply,
                "model": model
            }
        else:
            # When thinking is not enabled
            reply = response.content[0].text
            output = {
                "reply": reply,
                "model": model
            }
    except Exception as e:
        output = {
            "error": f"Failed to parse response: {str(e)}",
            "model": model
        }

    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Claude API")
    parser.add_argument("--model", default="claude-3-7-sonnet-20250219", help="Claude model to use")
    parser.add_argument("--prompt", required=True, help="Prompt to send to Claude")
    parser.add_argument("--enable-thinking", action="store_true", help="Enable thinking")
    args = parser.parse_args()
    
    response = query_claude_model(
        model=args.model,
        user_prompt=args.prompt,
        enable_thinking=args.enable_thinking
    )
    
    print(response)

