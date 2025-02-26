import os
import random

import openai
import torch
import transformers

GROQ_API_KEYS = [os.getenv("GROQ_API_KEY")]
OPENAI_API_KEYS = [os.getenv("OPENAI_API_KEY")]
AIGC_API_KEYS = [os.getenv("AIGC_API_KEY")]
LLAMA_API_KEYS = [os.getenv("LLAMA_API_KEY")]


def get_client(model, local=False):
    if local:
        return transformers.pipeline(
            "text-generation",
            model=model,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )

    if "gpt" in model:  # OpenAI API paid-request
        api_key = random.choice(OPENAI_API_KEYS)
        base_url = "https://api.openai.com/v1"
        print(f"Using API key: {api_key} @ {base_url}")
        return openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    else:  # LLAMAAPI paid-request
        api_key = random.choice(LLAMA_API_KEYS)
        base_url = "https://api.llama-api.com"
        print(f"Using API key: {api_key} @ {base_url}")
        return openai.OpenAI(api_key=api_key, base_url=base_url)


def get_completion(client, **kwargs):
    if isinstance(client, openai.OpenAI):
        outputs = client.chat.completions.create(**kwargs)
        # print(outputs)
        return outputs.choices[0].message.content.strip()
    else:
        raise NotImplementedError("support for transformers pipeline is coming soon~")
        # # Example: gemma-2-9b-it
        #
        # # remove system-role from messages
        # # since gemma2 does not support it natively
        # messages = kwargs.pop("messages", None)[1:]
        # kwargs.pop("model", None)  # remove param
        # kwargs["max_new_tokens"] = kwargs.pop("max_tokens", None)  # rename param

        # outputs = client(messages, do_sample=False, **kwargs)
        # return outputs[0]["generated_text"][-1]["content"].strip()
