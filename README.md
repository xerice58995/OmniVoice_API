## 快速啟動 Omnivoice

1. 建立環境:
   ```bash
   conda create -n omnivoice python=3.10
   conda activate omnivoice
   ```

2. 安裝omnivoice
    ```bash
   pip install omnivoice
   ```

3. 安裝依賴:
    ```bash
    # 建議先安裝對應顯卡的 PyTorch，例如:
    pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128
    # 安裝其餘依賴
    pip install -r requirements.txt
    ```

4. 啟動 API:
    ```bash
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

    啟動後請訪問：http://localhost:8000/docs 進入 Swagger UI 進行測試。

## 使用說明

OmniVoice的優勢為生成速度，據稱RTF as low as 0.025 (40x faster than real-time)。

OmniVoice共有兩種功能：

1. Voice Cloning
    上傳音源，經由模型克隆音色，並讀出需希望生成的文字
    OmniVoice只需要5秒左右樣本即可生成克隆
    需要克隆的音源和希望輸出的語言儘量保持相同(如果希望模型說中文，那餵給模型的音檔也儘量用中文)
    由於是中國研發的TTS模型，Prompt建議使用簡體中文以避免發音錯誤。

2. Voice Design
    於text處輸入希望TTS模型生成的語句
    於instruct填入希望的語調、性別等等prompt
    語調、性別等等prompt需要制式化格式，請參考 https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md
    由於是中國研發的TTS模型，Prompt建議使用簡體中文以避免發音錯誤。

3. 其他功能
    模型支援非語言發音，如嘆氣、大笑...等等
    模型支援中英發音細部微調，如：「这批货物打ZHE2出售」
    請參考原始模型[Github](https://github.com/k2-fsa/OmniVoice/tree/master)
    如僅需進行簡單功能測試，可以直接線上使用[ Hugging Face Demo  ](https://huggingface.co/spaces/k2-fsa/OmniVoice)
