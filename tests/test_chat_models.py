import sys, pathlib, time
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "app"))

from chat.chat_factory_options import ChatFactoryOptions # type: ignore
from chat.chat_factory import ChatFactory # type: ignore
from chat.listener import SendMessageListener # type: ignore


def create_factory_options(api_id: str, model: str, api_key_envvar: str) -> ChatFactoryOptions:
    return ChatFactoryOptions(
        api_id=api_id,
        model=model,
        temperature=None,
        instruction="response in one sentence.",
        bad_response="",
        history_size=5,
        history_char_limit=1000,
        api_timeout=30.0,
        api_key_envvar=api_key_envvar,
        api_endpoint_envvar="",
        api_base_url="",
        gemini_option={
            "safety_filter_harassment": "BLOCK_MEDIUM_AND_ABOVE",
            "safety_filter_hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
            "safety_filter_sexually_explicit": "BLOCK_MEDIUM_AND_ABOVE",
            "safety_filter_dangerous_content": "BLOCK_MEDIUM_AND_ABOVE"
        },
        claude_options={ "max_tokens": 4096, "extended_thinking": False, "budget_tokens": 2048 }
    )


def test_models(api_id: str, api_key_envvar: str, models: list, error_detail: bool=False):
    error_message = ""
    listener = SendMessageListener()
    def on_error(e, t, m=None):
        nonlocal error_message
        error_message = f" -> Error Type: {t}, Message: {m}, Exception: {e}"
        if not error_detail:
            error_message = error_message[:128]
    listener.on_error = on_error

    for model in models:
        option = create_factory_options(api_id, model, api_key_envvar)
        chat_client = ChatFactory.create(option)
        try:
            start = time.time()
            response =chat_client.send_message("Hello, this is a test message.", None, listener)
            end = time.time()
            elapsed_ms = (end - start) * 1000

            if response:
                print(f"😊 OK Model: {model}, Time: {elapsed_ms:.1f} ms, Response: {response}")
            else:
                print(f"💀 NG Model: {model}, Time: {elapsed_ms:.1f} ms, No response")
                if error_message:
                    print(error_message)
        except Exception as e:
            print(f"💀 NG Model: {model}, Error: {e}")


def test_openai(error_detail: bool=False):
    models = ["chat-latest", "gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna", "gpt-6-sol",
              "gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol",
              "gpt-5.5", "gpt-5.5-pro",
              "gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-5.4-pro",
              "gpt-5.3-codex", "gpt-5.2", "gpt-5.2-pro", "gpt-5.1",
              "gpt-5", "gpt-5-pro", "gpt-5-mini", "gpt-5-nano",
              "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o",
              "gpt-3.5-turbo", "o4-mini", "o3", "o3-mini", "o1"]

    print("\n=== Testing OpenAI Models...")
    test_models("OpenAI", "OPENAI_API_KEY", models, error_detail=error_detail)


def test_openai_new(error_detail: bool=False):
    models = ["gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna", "gpt-6-sol",
              "gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"]

    print("\n=== Testing OpenAI Models...")
    test_models("OpenAI", "OPENAI_API_KEY", models, error_detail=error_detail)


def test_openai_one(error_detail: bool=False):
    models = ["gpt-6.1-sol"]

    print("\n=== Testing OpenAI Models...")
    test_models("OpenAI", "OPENAI_API_KEY", models, error_detail=error_detail)


def test_claude(error_detail: bool=False):
    models = ["claude-fable-5-1", "claude-fable-5",
              "claude-opus-5-5", "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6", "claude-opus-4-5",
              "claude-sonnet-5-5", "claude-sonnet-4-6", "claude-sonnet-4-5",
              "claude-haiku-5-5", "claude-haiku-4-5"]
    
    print("\n=== Testing Claude Models...")
    test_models("Claude", "ANTHROPIC_API_KEY", models, error_detail=error_detail)


def test_claude_new(error_detail: bool=False):
    models = ["claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5"]
    
    print("\n=== Testing Claude Models...")
    test_models("Claude", "ANTHROPIC_API_KEY", models, error_detail=error_detail)


def test_claude_one(error_detail: bool=False):
    models = ["claude-fable-5"]
    
    print("\n=== Testing Claude Models...")
    test_models("Claude", "ANTHROPIC_API_KEY", models, error_detail=error_detail)


def test_gemini(error_detail: bool=False):
    models = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite",
              "gemini-3.1-pro-preview", "gemini-3.1-flash-lite",
              "gemini-3-flash-preview",
              "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
    
    print("\n=== Testing Gemini Models...")
    test_models("Gemini", "GEMINI_API_KEY", models, error_detail=error_detail)

def test_gemini_one(error_detail: bool=False):
    models = ["gemini-3.8-flash"]
    
    print("\n=== Testing Gemini Models...")
    test_models("Gemini", "GEMINI_API_KEY", models, error_detail=error_detail)


if __name__ == "__main__":
    #test_openai(error_detail=True)
    #test_claude(error_detail=True)
    test_gemini_one(error_detail=True)
