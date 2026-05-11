import os

import soundfile as sf
import torch
from omnivoice import OmniVoice


class OmniVoiceEngine:
    def __init__(self):
        self.model = None

    def load_model(self):
        self.model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice",
            device_map="cuda:0",
            cache_dir="./model_weights",
            dtype=torch.float16,
        )
        print(f"模型已成功載入至設備")

    def generate(self, **kwargs):
        if self.model is None:
            raise RuntimeError("模型尚未載入")
        audio_list = self.model.generate(**kwargs)
        wav = audio_list[0]
        return wav, 24000
