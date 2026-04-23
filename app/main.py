from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from app.core import OmniVoiceEngine
from contextlib import asynccontextmanager
from typing import Optional
import io, os, uuid, soundfile as sf
import torch
import gc


engine = OmniVoiceEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("正在載入 OmniVoice 模型至 GPU...")
    engine.load_model()
    yield
    print("正在關閉 API 並釋放顯存...")
    if engine.model is not None:
        engine.model = None

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect() # 進階清理：清理進程間通訊的顯存

app = FastAPI(lifespan=lifespan)


# -------------------------
# Voice Design
# 於text處輸入希望TTS模型生成的語句
# 於instruct填入希望的語調、性別等等prompt
# instruct需要只用制式化的prompt，請參考 https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md
# 由於是中國研發的TTS模型，Prompt建議使用簡體中文以避免發音錯誤。
# -------------------------

@app.post("/generate/voice_design")
async def voice_design(
    text: str = Form(
        ...,
        description="【必填】想要模型說出的文字內容，使用簡體中文以避免發音錯誤。",
        example="你好，我是一位虚拟助理，今天很高兴能够有这个机会认识各位，并和各位介绍功能。"
    ),
    instruct : Optional[str] = Form(
        None,
        description="【選填】希望的語調、性別等等，可留白。",
        example="女，青年，高音调"
    ),
):
    wav, sr = engine.generate(
            text=text,
            instruct=instruct,
        )
    return wav_to_stream(wav, sr)


# -------------------------
# Voice Cloning
# 於ref_audio載入希望克隆的音源
# OmniVoice只需要5秒左右樣本即可生成克隆
# 需要克隆的音源和希望輸出的語言儘量保持相同(如果希望模型說中文，那餵給模型的音檔也儘量用中文)
# -------------------------

@app.post("/generate/voice_cloning")
async def voice_cloning(
    text: str = Form(
        ...,
        description="【必填】想要模型說出的文字內容，使用簡體中文以避免發音錯誤。",
        example="你好，我是一位虚拟助理，今天很高兴能够有这个机会认识各位，并和各位介绍功能。"
    ),
    ref_audio: UploadFile = File(
        ...,
        description="【必填】參考音檔（樣本），5秒左右即可，可從Samples資料夾選取。",
    ),
    ref_text: Optional[str] = Form(
        None,
        description="【選填】上傳音檔的文字稿，可留白。",
        example="【選填】上傳音檔的文字稿。",
    )
):
    ref_path = await save_temp_file(ref_audio)

    try:
        wav, sr = engine.generate(
            text=text,
            ref_audio=ref_path,
            ref_text=ref_text,
        )
        return wav_to_stream(wav, sr)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(ref_path):
            os.remove(ref_path)
            print(f"已清理暫存檔: {ref_path}")



async def save_temp_file(upload_file: UploadFile):
    ext = os.path.splitext(upload_file.filename)[1]
    tmp_path = f"temp_{uuid.uuid4()}{ext}"
    with open(tmp_path, "wb") as buffer:
        buffer.write(await upload_file.read())
    return tmp_path

def wav_to_stream(wav, sr):
    buffer = io.BytesIO()
    sf.write(buffer, wav, sr, format='WAV')
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="audio/wav")
