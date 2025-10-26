"""
Audio Manager
Handles Speech-to-Text (STT), Text-to-Speech (TTS), and VAD-based recording operations.
Refactored to use YAML-based configuration following best practices.
"""

import traceback
import os
import wave
import time
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

from config.config_manager import get_config

# Conditional imports based on TTS engine configuration
config = get_config()

if config.config.tts.engine == "google":
    from google.cloud import texttospeech
elif config.config.tts.engine == "coqui":
    import torch
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
    from TTS.config.shared_configs import BaseDatasetConfig

from groq import Groq

# Lazy import for Silero VAD (only when needed)
_silero_vad_model = None


def get_silero_vad_model():
    """Lazy load Silero VAD model."""
    global _silero_vad_model
    if _silero_vad_model is None:
        try:
            import torch
            _silero_vad_model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            print("✅ Modelo Silero VAD carregado com sucesso.")
        except Exception as e:
            print(f"❌ ERRO ao carregar Silero VAD: {e}")
            _silero_vad_model = False  # Mark as failed
    return _silero_vad_model if _silero_vad_model is not False else None


class AudioManager:
    """
    Manages audio conversion between text and speech.

    Supports multiple TTS engines (Google Cloud TTS, Coqui TTS, ElevenLabs)
    and STT via Groq Whisper API.
    """

    def __init__(self, hardware_manager):
        """
        Initialize the audio manager.

        Args:
            hardware_manager: Hardware manager instance for LED/display feedback
        """
        self.config = get_config()
        self.hardware = hardware_manager
        self.tts_engine = self.config.config.tts.engine
        self.tts_model = None
        self.groq_client = None

        # Initialize STT
        self._init_stt()

        # Initialize TTS
        self._init_tts()

    def _init_stt(self):
        """Initialize Speech-to-Text client."""
        try:
            groq_api_key = self.config.get_api_key("groq")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found")

            self.groq_client = Groq(api_key=groq_api_key)
            print("✅ Cliente da Groq para Whisper (STT) inicializado.")
        except Exception as e:
            self.groq_client = None
            print(f"❌ ERRO ao inicializar cliente Groq: {e}")

    def _init_tts(self):
        """Initialize Text-to-Speech engine based on configuration."""
        print(f"🔊 Usando motor de voz (TTS): '{self.tts_engine}'")

        if self.tts_engine == "google":
            self._init_google_tts()
        elif self.tts_engine == "coqui":
            self._init_coqui_tts()
        elif self.tts_engine == "elevenlabs":
            self._init_elevenlabs_tts()
        else:
            print(f"⚠️  Motor TTS desconhecido: '{self.tts_engine}'")
            self.tts_engine = None

    def _init_google_tts(self):
        """Initialize Google Cloud TTS client."""
        try:
            self.tts_model = texttospeech.TextToSpeechClient()
            print("✅ Cliente Google Cloud TTS inicializado.")
        except Exception as e:
            print(f"❌ ERRO ao inicializar Google Cloud TTS: {e}")
            self.tts_engine = None

    def _init_coqui_tts(self):
        """Initialize Coqui TTS model."""
        print("⏳ Carregando modelo Coqui TTS (XTTSv2) na memória...")

        voice_sample_path = self.config.get_tts_voice_sample_path()
        if not voice_sample_path or not voice_sample_path.exists():
            print(f"❌ ERRO CRÍTICO: Arquivo de amostra de voz não encontrado em '{voice_sample_path}'")
            self.tts_engine = None
            return

        try:
            # Safe load for Coqui models
            torch.serialization.add_safe_globals([
                XttsConfig,
                XttsAudioConfig,
                XttsArgs,
                BaseDatasetConfig
            ])

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts_model = TTS(
                self.config.config.tts.coqui.model,
                gpu=(device == "cuda")
            )
            print(f"✅ Modelo Coqui TTS carregado com sucesso no dispositivo '{device}'.")
        except Exception as e:
            print(f"❌ ERRO ao carregar modelo Coqui TTS: {e}")
            traceback.print_exc()
            self.tts_engine = None

    def _init_elevenlabs_tts(self):
        """Initialize ElevenLabs TTS (placeholder for future implementation)."""
        print("⚠️  ElevenLabs TTS ainda não implementado.")
        self.tts_engine = None

    def record_with_vad(self, stream, audio_interface, clear_buffer: bool = True) -> Tuple[Optional[str], float]:
        """
        Record audio using Voice Activity Detection (VAD).
        Stops recording automatically when user stops speaking.

        Args:
            stream: PyAudio stream object
            audio_interface: PyAudio interface
            clear_buffer: Whether to clear buffer before recording

        Returns:
            Tuple of (audio_file_path, recording_duration_seconds)
        """
        vad_config = self.config.config.recording.vad

        if not vad_config.enabled:
            # Fallback to fixed duration recording
            return self._record_fixed_duration(stream, audio_interface, clear_buffer)

        # Load VAD model
        vad_model = get_silero_vad_model()
        if vad_model is None:
            print("⚠️  VAD não disponível, usando gravação com duração fixa.")
            return self._record_fixed_duration(stream, audio_interface, clear_buffer)

        import torch

        # Configuration
        sample_rate = self.config.config.recording.sample_rate

        # Silero-VAD expects 512 samples for 16kHz (32ms chunks)
        vad_chunk_size = 512 if sample_rate == 16000 else 256

        # Clear buffer (using original chunk size)
        if clear_buffer:
            original_chunk_size = self.config.config.recording.chunk_size
            for _ in range(4):
                try:
                    stream.read(original_chunk_size, exception_on_overflow=False)
                except:
                    pass

        print(f"🎤 Escutando... (VAD habilitado, máx {vad_config.max_recording_seconds}s)")

        # State tracking
        frames = []
        speech_frames = []
        is_speech_started = False
        silence_chunks = 0
        speech_chunks = 0

        # Calculate thresholds in chunks (using VAD chunk size)
        chunk_duration_ms = (vad_chunk_size / sample_rate) * 1000
        min_speech_chunks = int(vad_config.min_speech_duration_ms / chunk_duration_ms)
        min_silence_chunks = int(vad_config.min_silence_duration_ms / chunk_duration_ms)
        max_chunks = int(vad_config.max_recording_seconds * sample_rate / vad_chunk_size)
        speech_pad_chunks = int(vad_config.speech_pad_ms / chunk_duration_ms)

        start_time = time.time()

        try:
            while len(frames) < max_chunks:
                # Read audio chunk (512 samples for 16kHz)
                audio_chunk = stream.read(vad_chunk_size, exception_on_overflow=False)
                audio_array = np.frombuffer(audio_chunk, dtype=np.int16)

                # Convert to float32 for VAD model
                audio_float = audio_array.astype(np.float32) / 32768.0
                audio_tensor = torch.from_numpy(audio_float)

                # Get speech probability
                speech_prob = vad_model(audio_tensor, sample_rate).item()

                # Track all frames for potential inclusion
                frames.append(audio_chunk)

                # Speech detection logic
                if speech_prob >= vad_config.threshold:
                    speech_chunks += 1
                    silence_chunks = 0

                    if not is_speech_started and speech_chunks >= min_speech_chunks:
                        is_speech_started = True
                        print("   ✓ Fala detectada, gravando...")

                        # Include padding frames before speech
                        start_idx = max(0, len(frames) - speech_chunks - speech_pad_chunks)
                        speech_frames = frames[start_idx:]

                    elif is_speech_started:
                        speech_frames.append(audio_chunk)

                    # Progress indicator
                    elapsed = time.time() - start_time
                    print(f"   🔴 Gravando... {elapsed:.1f}s (confiança: {speech_prob:.2f})", end="\r")

                else:
                    speech_chunks = 0

                    if is_speech_started:
                        silence_chunks += 1
                        speech_frames.append(audio_chunk)

                        # Check if silence threshold reached
                        if silence_chunks >= min_silence_chunks:
                            print(" " * 60, end="\r")
                            print(f"   ✓ Silêncio detectado, finalizando gravação.")
                            break

        except KeyboardInterrupt:
            print("\n   Gravação interrompida pelo usuário.")

        recording_duration = time.time() - start_time

        # Save recording
        if is_speech_started and speech_frames:
            output_path = str(self.config.get_path('temp_audio'))

            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(self.config.config.recording.channels)
                wf.setsampwidth(audio_interface.get_sample_size(2))  # paInt16 = 2
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(speech_frames))

            print(f"✅ Gravação concluída ({recording_duration:.1f}s, {len(speech_frames)} chunks)")
            return output_path, recording_duration

        else:
            print("⚠️  Nenhuma fala detectada.")
            return None, recording_duration

    def _record_fixed_duration(self, stream, audio_interface, clear_buffer: bool = True) -> Tuple[Optional[str], float]:
        """
        Fallback: Record audio for a fixed duration.

        Args:
            stream: PyAudio stream object
            audio_interface: PyAudio interface
            clear_buffer: Whether to clear buffer before recording

        Returns:
            Tuple of (audio_file_path, recording_duration_seconds)
        """
        sample_rate = self.config.config.recording.sample_rate
        chunk_size = self.config.config.recording.chunk_size
        duration = self.config.config.recording.duration_seconds

        # Clear buffer
        if clear_buffer:
            for _ in range(4):
                try:
                    stream.read(chunk_size, exception_on_overflow=False)
                except:
                    pass

        print(f"🎤 Gravando por {duration} segundos...")
        frames = []

        start_time = time.time()
        for _ in range(0, int(sample_rate / chunk_size * duration)):
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)

        recording_duration = time.time() - start_time

        # Save recording
        output_path = str(self.config.get_path('temp_audio'))

        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(self.config.config.recording.channels)
            wf.setsampwidth(audio_interface.get_sample_size(2))  # paInt16 = 2
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))

        print(f"✅ Gravação concluída ({recording_duration:.1f}s)")
        return output_path, recording_duration

    def transcribe_from_file(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file to text using Groq Whisper.

        Args:
            audio_file_path: Path to audio file

        Returns:
            Transcribed text or None if error
        """
        if not self.groq_client:
            return self.config.prompts.responses["audio_system_offline"]

        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model=self.config.config.stt.model,
                    language=self.config.config.stt.language
                )
            return transcription.text
        except Exception as e:
            print(f"❌ ERRO ao transcrever com Whisper/Groq: {e}")
            traceback.print_exc()
            return None

    def text_to_speech_file(self, text: str) -> Optional[str]:
        """
        Convert text to speech and save to file.

        Args:
            text: Text to convert to speech

        Returns:
            Path to generated audio file or None if error
        """
        if not self.tts_engine:
            print(f"   ⚠️ {self.config.prompts.responses['tts_offline']}")
            return None

        print(f"   Gerando áudio com o motor '{self.tts_engine}'...")

        if self.tts_engine == "google":
            return self._tts_google(text)
        elif self.tts_engine == "coqui":
            return self._tts_coqui(text)

        return None

    def _tts_google(self, text: str) -> Optional[str]:
        """
        Generate speech using Google Cloud TTS.

        Args:
            text: Text to convert

        Returns:
            Path to generated MP3 file
        """
        output_filename = str(self.config.get_path('response_audio_mp3'))

        try:
            google_config = self.config.config.tts.google

            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=google_config.language_code,
                name=google_config.voice_name
            )

            # Map string encoding to enum
            encoding_map = {
                "MP3": texttospeech.AudioEncoding.MP3,
                "LINEAR16": texttospeech.AudioEncoding.LINEAR16,
                "OGG_OPUS": texttospeech.AudioEncoding.OGG_OPUS
            }
            audio_encoding = encoding_map.get(
                google_config.audio_encoding,
                texttospeech.AudioEncoding.MP3
            )

            audio_config = texttospeech.AudioConfig(audio_encoding=audio_encoding)

            response = self.tts_model.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            with open(output_filename, "wb") as out:
                out.write(response.audio_content)

            return output_filename

        except Exception as e:
            print(f"❌ ERRO no motor Google TTS: {e}")
            traceback.print_exc()
            return None

    def _tts_coqui(self, text: str) -> Optional[str]:
        """
        Generate speech using Coqui TTS.

        Args:
            text: Text to convert

        Returns:
            Path to generated WAV file
        """
        output_filename = str(self.config.get_path('response_audio_wav'))

        try:
            coqui_config = self.config.config.tts.coqui
            voice_sample_path = str(self.config.get_tts_voice_sample_path())

            self.tts_model.tts_to_file(
                text=text,
                file_path=output_filename,
                speaker_wav=voice_sample_path,
                language=coqui_config.language,
                split_sentences=coqui_config.split_sentences
            )

            return output_filename

        except Exception as e:
            print(f"❌ ERRO no motor Coqui TTS: {e}")
            traceback.print_exc()
            return None
