import queue
import sys
import collections

import numpy as np
import sounddevice as sd
import webrtcvad

def find_input_device(name_contains="PD200X"):
    devices = sd.query_devices()

    for index, device in enumerate(devices):
        name = device["name"]
        max_inputs = device["max_input_channels"]

        if name_contains.lower() in name.lower() and max_inputs > 0:
            print(f"🎤 Using mic: {index} - {name}")
            return index

    raise RuntimeError(f"No input device found containing: {name_contains}")


# Optional debug saving
DEBUG_SAVE_AUDIO = False

if DEBUG_SAVE_AUDIO:
    import soundfile as sf

MIC_INDEX = find_input_device("PD200X")
SAMPLE_RATE = 48000
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
BYTES_PER_SAMPLE = 2  # 16-bit int16
CHANNELS = 1

vad = webrtcvad.Vad(3)  # aggressiveness: 0-3
q = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)

    # sounddevice gives float32 by default, convert to int16 PCM bytes
    audio = (indata[:, 0] * 32767).astype(np.int16).tobytes()
    q.put(audio)


def frame_generator():
    buf = b""
    bytes_per_frame = FRAME_SIZE * BYTES_PER_SAMPLE

    while True:
        chunk = q.get()

        if chunk is None:
            return

        buf += chunk

        while len(buf) >= bytes_per_frame:
            frame = buf[:bytes_per_frame]
            buf = buf[bytes_per_frame:]
            yield frame


def vad_collector():
    """
    Collects speech using WebRTC VAD with a ring buffer.

    Returns one complete speech segment as bytes when speech ends.
    """
    padding_duration_ms = 300
    num_padding_frames = int(padding_duration_ms / FRAME_DURATION_MS)

    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []

    for frame in frame_generator():
        is_speech = vad.is_speech(frame, SAMPLE_RATE)

        if not triggered:
            ring_buffer.append((frame, is_speech))

            num_voiced = len([f for f, speech in ring_buffer if speech])

            if num_voiced > 0.8 * ring_buffer.maxlen:
                print("🎙️ Speech started")
                triggered = True

                for f, speech in ring_buffer:
                    voiced_frames.append(f)

                ring_buffer.clear()

        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))

            num_unvoiced = len([f for f, speech in ring_buffer if not speech])

            if num_unvoiced > 0.8 * ring_buffer.maxlen:
                print("🛑 Speech ended")

                triggered = False

                segment = b"".join(voiced_frames)

                ring_buffer.clear()
                voiced_frames = []

                yield segment

def listen_until_silence():
    with sd.InputStream(
        device=MIC_INDEX,
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        dtype="float32",
        callback=audio_callback,
        blocksize=FRAME_SIZE,
    ):
        print("Listening for speech...")

        for segment in vad_collector():
            return segment

def main():
    try:
        while True:
            segment = listen_until_silence()

            if segment:
                print(f"Detected speech segment: {len(segment)} bytes")

                if DEBUG_SAVE_AUDIO:
                    data = np.frombuffer(segment, dtype=np.int16).astype(np.float32) / 32767.0
                    sf.write("test_segment.wav", data, SAMPLE_RATE)

    except KeyboardInterrupt:
        print("\nStopping listener...")

    finally:
        q.put(None)


if __name__ == "__main__":
    main()
