import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def load_model(model_name, precision):
    kwargs = {"device_map": "auto"}

    if precision == "fp16":
        kwargs["torch_dtype"] = torch.float16
    elif precision == "int8":
        kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    elif precision == "int4":
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
    else:
        raise ValueError(f"unknown precision: {precision}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)
    return tokenizer, model

class ModelAgent:
    def __init__(self, tokenizer, model, system_prompt, max_new_tokens=120):
        self.tokenizer = tokenizer
        self.model = model
        self.system_prompt = system_prompt
        self.max_new_tokens = max_new_tokens

    def reply(self, transcript):
        messages = [{"role": "system", "content": self.system_prompt}]
        for speaker, text in transcript:
            role = "assistant" if speaker == "A" else "user"
            messages.append({"role": role, "content": text})

        if len(transcript) == 0:
            messages.append({"role": "user", "content": "Make your opening offer."})

        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        output = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
        )
        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)