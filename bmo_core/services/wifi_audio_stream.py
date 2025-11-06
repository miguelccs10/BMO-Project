"""
Wi-Fi Audio Stream Manager
Manages audio streaming from phone to Jetson via Wi-Fi (WO Mic, SoundWire, etc.)
"""

import subprocess
import re
import time
from typing import Optional, Dict, List, Tuple
from pathlib import Path


class WiFiAudioStreamManager:
    """
    Manages Wi-Fi audio streaming devices for BMO.

    Supports:
    - WO Mic (recommended for Linux)
    - SoundWire
    - Manual device specification
    """

    def __init__(self):
        """Initialize Wi-Fi audio stream manager."""
        self.detected_device = None
        self.device_index = None
        self.device_name = None
        self.stream_type = None

    def detect_wifi_stream_device(self, preferred_names: List[str] = None) -> Optional[int]:
        """
        Detect Wi-Fi streaming audio device automatically.

        Args:
            preferred_names: List of device name patterns to search for

        Returns:
            PyAudio device index if found, None otherwise
        """
        if preferred_names is None:
            preferred_names = [
                "wo_mic",
                "WO Mic",
                "soundwire",
                "SoundWire",
                "phone",
                "Phone",
                "stream",
                "Stream"
            ]

        print("🔍 Procurando dispositivo de stream Wi-Fi...")

        # Try to detect using PyAudio
        try:
            import pyaudio
            pa = pyaudio.PyAudio()

            for i in range(pa.get_device_count()):
                device_info = pa.get_device_info_by_index(i)
                device_name = device_info.get('name', '').lower()
                max_input_channels = device_info.get('maxInputChannels', 0)

                # Check if it's an input device
                if max_input_channels > 0:
                    # Check against preferred names
                    for pattern in preferred_names:
                        if pattern.lower() in device_name:
                            self.device_index = i
                            self.device_name = device_info['name']
                            self.stream_type = pattern

                            pa.terminate()
                            print(f"✅ Dispositivo Wi-Fi encontrado: [{i}] {self.device_name}")
                            return i

            pa.terminate()
            print("⚠️  Nenhum dispositivo de stream Wi-Fi detectado automaticamente.")
            return None

        except Exception as e:
            print(f"❌ Erro ao detectar dispositivo: {e}")
            return None

    def get_pulseaudio_sources(self) -> List[Dict[str, str]]:
        """
        Get list of PulseAudio/PipeWire sources.

        Returns:
            List of source dictionaries with name and description
        """
        sources = []

        try:
            result = subprocess.run(
                ["pactl", "list", "sources", "short"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sources.append({
                            'index': parts[0],
                            'name': parts[1],
                            'description': parts[2] if len(parts) > 2 else parts[1]
                        })

        except Exception as e:
            print(f"⚠️  Não foi possível listar fontes PulseAudio: {e}")

        return sources

    def find_wifi_stream_in_pulseaudio(self) -> Optional[str]:
        """
        Find Wi-Fi stream device in PulseAudio/PipeWire.

        Returns:
            Source name if found, None otherwise
        """
        sources = self.get_pulseaudio_sources()

        # Common patterns for Wi-Fi streaming apps
        patterns = [
            r"wo.?mic",
            r"soundwire",
            r"phone",
            r"stream",
            r"network.*audio",
            r"wifi.*mic"
        ]

        for source in sources:
            source_name = source['name'].lower()
            source_desc = source['description'].lower()

            for pattern in patterns:
                if re.search(pattern, source_name) or re.search(pattern, source_desc):
                    print(f"✅ Encontrado no PulseAudio: {source['name']}")
                    return source['name']

        return None

    def is_womic_running(self) -> bool:
        """
        Check if WO Mic client is running.

        Returns:
            True if running, False otherwise
        """
        try:
            result = subprocess.run(
                ["pgrep", "-f", "womic"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def start_womic_client(self, server_ip: str = None, port: int = 48000) -> bool:
        """
        Start WO Mic client (if installed).

        Args:
            server_ip: IP address of phone running WO Mic server
            port: Port number (default: 48000 for Wi-Fi mode)

        Returns:
            True if started successfully, False otherwise
        """
        if not Path("/usr/bin/womic").exists():
            print("❌ WO Mic client não está instalado.")
            print("   Execute: bash requirements/setup_wifi_audio.sh")
            return False

        if self.is_womic_running():
            print("✅ WO Mic client já está rodando.")
            return True

        # Auto-detect server IP if not provided
        if server_ip is None:
            server_ip = self._detect_phone_ip()
            if not server_ip:
                print("❌ Não foi possível detectar IP do celular.")
                print("   Conecte o celular ao hotspot e tente novamente.")
                return False

        print(f"🔄 Iniciando WO Mic client (conectando a {server_ip}:{port})...")

        try:
            # Start WO Mic in background
            subprocess.Popen(
                ["womic", "-t", "0", "-i", server_ip, "-p", str(port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait a bit for connection
            time.sleep(2)

            if self.is_womic_running():
                print("✅ WO Mic client iniciado com sucesso.")
                return True
            else:
                print("❌ Falha ao iniciar WO Mic client.")
                return False

        except Exception as e:
            print(f"❌ Erro ao iniciar WO Mic: {e}")
            return False

    def _detect_phone_ip(self) -> Optional[str]:
        """
        Try to detect phone's IP address on local network.

        Returns:
            IP address if found, None otherwise
        """
        try:
            # Get default gateway (likely the phone if using hotspot)
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                # Parse output: "default via 192.168.43.1 dev wlan0 ..."
                match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                if match:
                    gateway_ip = match.group(1)
                    print(f"   📱 Detectado gateway (provável IP do celular): {gateway_ip}")
                    return gateway_ip

        except Exception as e:
            print(f"⚠️  Erro ao detectar IP: {e}")

        return None

    def get_recommended_device_index(self) -> Optional[int]:
        """
        Get recommended PyAudio device index for Wi-Fi streaming.

        Returns:
            Device index if found, None otherwise
        """
        if self.device_index is not None:
            return self.device_index

        # Try auto-detection
        return self.detect_wifi_stream_device()

    def print_status(self):
        """Print current Wi-Fi audio stream status."""
        print("\n" + "="*60)
        print("📡 Wi-Fi Audio Stream Status")
        print("="*60)

        if self.device_index is not None:
            print(f"✅ Dispositivo Detectado: [{self.device_index}] {self.device_name}")
            print(f"   Tipo: {self.stream_type}")
        else:
            print("⚠️  Nenhum dispositivo detectado")

        print(f"\n🔧 WO Mic Client: {'✅ Rodando' if self.is_womic_running() else '❌ Parado'}")

        # Show PulseAudio sources
        sources = self.get_pulseaudio_sources()
        if sources:
            print(f"\n🎤 Fontes de Áudio Disponíveis ({len(sources)}):")
            for source in sources[:5]:  # Show first 5
                print(f"   [{source['index']}] {source['name']}")

        print("="*60 + "\n")

    def setup_audio_device(self, auto_start: bool = True) -> Tuple[Optional[int], str]:
        """
        Complete setup for Wi-Fi audio streaming.

        Args:
            auto_start: Automatically start WO Mic if not running

        Returns:
            Tuple of (device_index, status_message)
        """
        print("\n🚀 Configurando entrada de áudio via Wi-Fi...")

        # Check if WO Mic is running
        if not self.is_womic_running():
            if auto_start:
                print("⏳ WO Mic não detectado. Tentando iniciar...")
                if not self.start_womic_client():
                    return None, "Falha ao iniciar WO Mic. Configure manualmente."
            else:
                return None, "WO Mic não está rodando. Inicie-o manualmente."

        # Wait a bit for audio device to appear
        time.sleep(1)

        # Detect device
        device_index = self.detect_wifi_stream_device()

        if device_index is not None:
            return device_index, f"Sucesso! Usando dispositivo [{device_index}] {self.device_name}"
        else:
            return None, "Dispositivo de stream não encontrado. Verifique se o app está transmitindo."


# Standalone utility functions for quick access
def quick_detect() -> Optional[int]:
    """Quick detection of Wi-Fi stream device."""
    manager = WiFiAudioStreamManager()
    return manager.detect_wifi_stream_device()


def quick_status():
    """Quick status check."""
    manager = WiFiAudioStreamManager()
    manager.print_status()


if __name__ == "__main__":
    # Quick diagnostic when run directly
    print("🔧 Wi-Fi Audio Stream - Diagnostic Tool\n")

    manager = WiFiAudioStreamManager()
    manager.print_status()

    # Try to detect device
    device_index = manager.detect_wifi_stream_device()

    if device_index is not None:
        print(f"\n✅ Recomendação: Use input_device_index: {device_index} no config.yaml")
    else:
        print("\n⚠️  Nenhum dispositivo detectado. Verifique:")
        print("   1. WO Mic app está rodando no celular")
        print("   2. Celular conectado na mesma rede (ou via hotspot)")
        print("   3. WO Mic client está instalado na Jetson")
        print("\n   Para instalar: bash requirements/setup_wifi_audio.sh")
