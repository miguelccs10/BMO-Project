# bmo_core/wake_word_detector.py
# (Versão 1.0 - Detector de Wake Word com Picovoice)

import os
import pvporcupine
import pyaudio
import struct
from . import config

class WakeWordDetector:
    def __init__(self, on_wake_word_callback):
        self.on_wake_word_callback = on_wake_word_callback
        self.porcupine = None
        self.pa = None
        self.audio_stream = None

    def start(self):
        try:
            model_dir = os.path.join(os.path.dirname(__file__), '..', 'picovoice_models')

            model_file_path = os.path.join(model_dir, 'porcupine_params_pt.pv')

            keyword_paths = [os.path.join(os.path.dirname(__file__), '..', 'picovoice_models', 'Ei-Bimo-raspberry.ppn')]

            self.porcupine = pvporcupine.create(
                access_key=config.PICOVOICE_ACCESS_KEY,
                model_path=model_file_path,
                keyword_paths=keyword_paths,
            )
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            print(f"BMO está escutando! Diga '{' ou '.join(config.WAKE_WORDS)}'.")
            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    print(f"Palavra de ativação '{config.WAKE_WORDS[keyword_index]}' detectada!")
                    self.on_wake_word_callback()

        except Exception as e:
            print(f"Erro no detector de wake word: {e}")
        finally:
            self.stop()

    def stop(self):
        if self.porcupine:
            self.porcupine.delete()
        if self.audio_stream:
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()