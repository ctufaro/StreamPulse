import audioop
import pyaudio

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024

audio = pyaudio.PyAudio()

print("\nInput devices:")
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    if info.get("maxInputChannels", 0) > 0:
        print(
            f"{i}: {info['name']} | "
            f"inputs={info['maxInputChannels']} | "
            f"default_rate={info['defaultSampleRate']}"
        )

print("\nOpening default mic...\n")

stream = audio.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=CHUNK_SIZE,
)

try:
    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        rms = audioop.rms(data, 2)

        bars = "#" * min(60, rms // 100)
        print(f"\rRMS: {rms:<6} {bars}", end="", flush=True)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
