import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import requests
import subprocess
import numpy as np
import wave

# ==============================

# CONFIG

# ==============================

MIC_INDEX = 45        # PD200X WASAPI mic
fs = 48000            # your mic works at 48k
duration = 4          # seconds per recording

PI_URL = "http://192.168.1.133:11434/api/generate"

# Load Whisper once

model = WhisperModel("base", device="cpu", compute_type="int8")

# ==============================

# FUNCTIONS

# ==============================

def listen():
print("\n🎤 Speak...")

```
recording = sd.rec(
    int(duration * fs),
    samplerate=fs,
    channels=1,
    dtype='int16',
    device=MIC_INDEX
)

sd.wait()

write("input.wav", fs, recording)

segments, _ = model.transcribe("input.wav")

text = "".join([s.text for s in segments]).strip()

return text
```

def ask_ember(prompt):
try:
response = requests.post(
PI_URL,
json={
"model": "phi3",
"prompt": prompt,
"stream": False
},
timeout=60
)

```
    data = response.json()
    return data.get("response", "").strip()

except Exception as e:
    print("❌ Error talking to Ember:", e)
    return ""
```

def speak(text):
if not text:
return

```
with open("tts_input.txt", "w", encoding="utf-8") as f:
    f.write(text)

subprocess.run(
    'piper --model en_GB-southern_english_female-low '
    '--input_file tts_input.txt --output_file output.wav',
    shell=True
)

# play audio directly
with wave.open("output.wav", 'rb') as wf:
    audio = wf.readframes(wf.getnframes())
    audio_np = np.frombuffer(audio, dtype=np.int16)

    sd.play(audio_np, samplerate=wf.getframerate())
    sd.wait()
```

# ==============================

# MAIN LOOP

# ==============================

print("🔥 Ember Voice System Ready")

while True:
user_input = listen()

```
if not user_input:
    print("⚠️ Didn't catch that...")
    continue

print("🧠 You:", user_input)

response = ask_ember(user_input)

print("🔥 Ember:", response)

speak(response)
```
