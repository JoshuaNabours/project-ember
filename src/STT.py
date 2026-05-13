import subprocess
import sounddevice as sd
import numpy as np
import wave
import requests

PI_URL = "http://192.168.1.133:11434/api/generate"

# ------------------

# LLM

# ------------------

def ask_ember(prompt):
response = requests.post(PI_URL, json={
"model": "phi3",
"prompt": prompt,
"stream": False
})

```
data = response.json()
return data.get("response", "Hmm... something went wrong.")
```

# ------------------

# TTS

# ------------------

def speak(text):
with open("tts_input.txt", "w", encoding="utf-8") as f:
f.write(text.strip())

```
subprocess.run(
    'piper --model en_GB-southern_english_female-low.onnx '
    '--input_file tts_input.txt --output_file output.wav',
    shell=True,
    check=True
)

# 🔊 play wav directly (no external app)
with wave.open("output.wav", 'rb') as wf:
    data = wf.readframes(wf.getnframes())
    audio = np.frombuffer(data, dtype=np.int16)

    sd.play(audio, samplerate=wf.getframerate())
    sd.wait()
```

# ------------------

# MAIN LOOP

# ------------------

while True:
user_input = input("You: ")

```
if user_input.lower() in ["exit", "quit"]:
    break

response = ask_ember(user_input)
print("Ember:", response)

speak(response)
```
