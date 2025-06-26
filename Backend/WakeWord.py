import pvporcupine
import pyaudio
import numpy as np
import threading
import asyncio
from dotenv import dotenv_values

class WakeWordDetector:
    def __init__(self, callback=None, loop=None):
        self.callback = callback
        try:
            self.loop = loop or asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        self.running = False
        self.is_processing = False
        self.thread = None
        self.porcupine = None
        self.stream = None
        self.pa = None

    def start_listening(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._listen, daemon=True)
            self.thread.start()

    def stop_listening(self):
        self.running = False

    def _listen(self):
        try:
            env = dotenv_values(".env")
            key = env.get("PorcupineKey")
            self.porcupine = pvporcupine.create(access_key=key, keywords=["jarvis"])

            self.pa = pyaudio.PyAudio()
            self.stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )

            print("🎙️ Wake word listener is running... Say 'Jarvis'")

            while self.running:
                pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)

                if self.porcupine.process(pcm) >= 0 and not self.is_processing:
                    print("🟢 Wake word detected!")
                    self.is_processing = True

                    # ✅ Pause the wake word stream so speech recognition can access the mic
                    self.stream.stop_stream()

                    try:
                        if asyncio.iscoroutinefunction(self.callback):
                            asyncio.run_coroutine_threadsafe(self.callback(), self.loop)
                        else:
                            self.callback()
                    except Exception as e:
                        print(f"[Callback Error] {e}")
                    finally:
                        # ✅ Resume the wake word stream
                        self.stream.start_stream()
                        self.is_processing = False

        except Exception as e:
            print(f"[WakeWordDetector ERROR] {e}")

        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.pa:
                self.pa.terminate()
            if self.porcupine:
                self.porcupine.delete()