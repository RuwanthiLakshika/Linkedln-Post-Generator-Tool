from langchain_groq import ChatGroq
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT_MODEL = "openai/gpt-oss-120b"

FALLBACK_MODEL_OPTIONS = {
    "GPT-OSS 120B (recommended for quality)": "openai/gpt-oss-120b",
    "GPT-OSS 20B (recommended for speed)": "openai/gpt-oss-20b",
}

RECOMMENDED_MODELS = {
    "openai/gpt-oss-120b": "recommended for quality",
    "openai/gpt-oss-20b": "recommended for speed",
}

NON_TEXT_MODEL_PREFIXES = (
    "whisper-",
    "canopylabs/",
    "meta-llama/llama-prompt-guard-",
)


def get_model_options():
    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        models = groq_client.models.list().data
        text_models = [
            model.id
            for model in models
            if model.active
            and not model.id.startswith(NON_TEXT_MODEL_PREFIXES)
            and model.id != "openai/gpt-oss-safeguard-20b"
        ]
        text_models.sort(key=lambda model_id: (model_id not in RECOMMENDED_MODELS, model_id))
        return {
            model_label(model_id): model_id
            for model_id in text_models
        }
    except Exception:
        return FALLBACK_MODEL_OPTIONS


def model_label(model_id):
    label = model_id.replace("/", " / ").replace("-", " ").title()
    recommendation = RECOMMENDED_MODELS.get(model_id)
    if recommendation:
        label += f" ({recommendation})"
    return label


def get_llm(model_name=DEFAULT_MODEL):
    return ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name=model_name)


def invoke_with_usage(prompt, model_name):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to the .env file.")

    response = Groq(api_key=api_key).chat.completions.with_raw_response.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
    )
    completion = response.parse()
    usage = completion.usage
    headers = response.headers
    return completion.choices[0].message.content, {
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "limit_tokens": headers.get("x-ratelimit-limit-tokens"),
        "remaining_tokens": headers.get("x-ratelimit-remaining-tokens"),
        "reset_tokens": headers.get("x-ratelimit-reset-tokens"),
    }


llm = get_llm()


if __name__ == "__main__":
    response = llm.invoke("Two most important ingradient in samosa are ")
    print(response.content)





