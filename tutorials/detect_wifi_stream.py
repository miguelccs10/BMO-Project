#!/usr/bin/env python3
"""
Wi-Fi Audio Stream Detector
Detects and tests Wi-Fi streaming audio devices (WO Mic, SoundWire, etc.)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pyaudio
import numpy as np
import wave
from bmo_core.services.wifi_audio_stream import WiFiAudioStreamManager


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def list_all_audio_devices():
    """List all audio input devices."""
    print_header("📋 Todos os Dispositivos de Entrada")

    pa = pyaudio.PyAudio()

    input_devices = []

    for i in range(pa.get_device_count()):
        device_info = pa.get_device_info_by_index(i)
        max_input_channels = device_info.get('maxInputChannels', 0)

        if max_input_channels > 0:
            input_devices.append({
                'index': i,
                'name': device_info['name'],
                'channels': max_input_channels,
                'sample_rate': int(device_info['defaultSampleRate'])
            })

    if not input_devices:
        print("❌ Nenhum dispositivo de entrada encontrado!")
        pa.terminate()
        return

    print(f"\n✅ Encontrados {len(input_devices)} dispositivos de entrada:\n")
    print(f"{'IDX':<5} {'NOME':<50} {'CH':<5} {'RATE':<10}")
    print("-" * 70)

    for device in input_devices:
        print(f"{device['index']:<5} {device['name']:<50} {device['channels']:<5} {device['sample_rate']:<10}")

    pa.terminate()


def detect_wifi_stream():
    """Detect Wi-Fi streaming devices."""
    print_header("🔍 Detectando Dispositivos de Stream Wi-Fi")

    manager = WiFiAudioStreamManager()

    # Show status
    manager.print_status()

    # Try detection
    device_index = manager.detect_wifi_stream_device()

    if device_index is not None:
        print(f"\n{'-' * 70}")
        print(f"✅ DISPOSITIVO WI-FI ENCONTRADO!")
        print(f"{'-' * 70}")
        print(f"   Índice: {device_index}")
        print(f"   Nome: {manager.device_name}")
        print(f"   Tipo: {manager.stream_type}")
        print(f"\n💡 Para usar no BMO, adicione no config.yaml:")
        print(f"   recording:")
        print(f"     input_device_index: {device_index}")
        print(f"{'-' * 70}\n")
        return device_index
    else:
        print(f"\n{'-' * 70}")
        print(f"⚠️  NENHUM DISPOSITIVO WI-FI DETECTADO")
        print(f"{'-' * 70}")
        print(f"\n💡 Verifique:")
        print(f"   1. WO Mic app está rodando no celular")
        print(f"   2. App está transmitindo (botão 'Start' pressionado)")
        print(f"   3. Celular e Jetson estão na mesma rede")
        print(f"   4. WO Mic client está instalado: bash requirements/setup_wifi_audio.sh")
        print(f"{'-' * 70}\n")
        return None


def test_audio_recording(device_index, duration=3):
    """Test audio recording from specified device."""
    print_header(f"🎤 Testando Gravação - Dispositivo [{device_index}]")

    pa = pyaudio.PyAudio()

    # Get device info
    try:
        device_info = pa.get_device_info_by_index(device_index)
        print(f"\n📱 Dispositivo: {device_info['name']}")
        print(f"   Sample Rate: {int(device_info['defaultSampleRate'])} Hz")
        print(f"   Canais: {device_info['maxInputChannels']}")
    except Exception as e:
        print(f"❌ Erro ao acessar dispositivo: {e}")
        pa.terminate()
        return False

    # Recording settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    print(f"\n🔴 Gravando por {duration} segundos...")
    print("   Fale alguma coisa ou faça ruído próximo ao celular!\n")

    frames = []

    try:
        # Open stream
        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=device_index
        )

        # Record
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            # Show progress
            progress = (i + 1) / int(RATE / CHUNK * duration) * 100
            print(f"   Gravando... {progress:.0f}%", end='\r')

        print("\n\n✅ Gravação concluída!")

        # Stop stream
        stream.stop_stream()
        stream.close()

        # Analyze audio
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        max_amplitude = np.max(np.abs(audio_data))
        rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))

        print(f"\n📊 Análise do Áudio:")
        print(f"   Amplitude Máxima: {max_amplitude} / 32768")
        print(f"   RMS: {rms:.2f}")

        if max_amplitude < 100:
            print(f"\n   ⚠️  Áudio muito baixo! Verifique:")
            print(f"      - Volume do celular está alto?")
            print(f"      - App WO Mic está realmente transmitindo?")
            print(f"      - Dispositivo correto selecionado?")
        elif max_amplitude < 1000:
            print(f"\n   🟡 Áudio detectado, mas baixo. Considere aumentar volume.")
        else:
            print(f"\n   ✅ Áudio detectado com boa amplitude!")

        # Save test file
        test_file = "/tmp/wifi_stream_test.wav"
        wf = wave.open(test_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pa.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"\n💾 Áudio salvo em: {test_file}")
        print(f"   Reproduza com: aplay {test_file}")

    except Exception as e:
        print(f"\n❌ Erro durante gravação: {e}")
        pa.terminate()
        return False

    pa.terminate()
    return True


def check_womic_status():
    """Check if WO Mic client is running."""
    print_header("🔧 Status do WO Mic Client")

    import subprocess

    # Check if womic is installed
    try:
        result = subprocess.run(
            ["which", "womic"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            womic_path = result.stdout.strip()
            print(f"\n✅ WO Mic instalado: {womic_path}")
        else:
            print(f"\n❌ WO Mic NÃO instalado")
            print(f"   Instale com: bash requirements/setup_wifi_audio.sh")
            return False
    except Exception as e:
        print(f"\n❌ Erro ao verificar instalação: {e}")
        return False

    # Check if womic is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "womic"],
            capture_output=True
        )

        if result.returncode == 0:
            print(f"✅ WO Mic client está RODANDO")

            # Get process info
            pid_result = subprocess.run(
                ["pgrep", "-af", "womic"],
                capture_output=True,
                text=True
            )
            print(f"\n📋 Processos:")
            for line in pid_result.stdout.strip().split('\n'):
                print(f"   {line}")

        else:
            print(f"⚠️  WO Mic client NÃO está rodando")
            print(f"\n💡 Para iniciar:")
            print(f"   womic -t 0 -i <IP_DO_CELULAR> -p 48000")
            print(f"\n   Exemplo:")
            print(f"   womic -t 0 -i 192.168.43.1 -p 48000")

    except Exception as e:
        print(f"\n⚠️  Erro ao verificar processo: {e}")

    # Check kernel module
    try:
        result = subprocess.run(
            ["lsmod"],
            capture_output=True,
            text=True
        )

        if "snd_aloop" in result.stdout:
            print(f"\n✅ Módulo do kernel (snd-aloop) carregado")
        else:
            print(f"\n⚠️  Módulo do kernel (snd-aloop) NÃO carregado")
            print(f"   Carregue com: sudo modprobe snd-aloop")

    except Exception as e:
        print(f"\n⚠️  Erro ao verificar módulo: {e}")

    print()
    return True


def interactive_menu():
    """Interactive menu for testing."""
    while True:
        print("\n" + "=" * 70)
        print("  🎯 Wi-Fi Audio Stream - Menu Interativo")
        print("=" * 70)
        print("\n  Escolha uma opção:\n")
        print("  1. 📋 Listar todos dispositivos de áudio")
        print("  2. 🔍 Detectar dispositivo Wi-Fi stream")
        print("  3. 🎤 Testar gravação de dispositivo específico")
        print("  4. 🔧 Verificar status do WO Mic")
        print("  5. 🚀 Detecção e teste completo")
        print("  0. ❌ Sair")
        print()

        try:
            choice = input("  Opção: ").strip()

            if choice == "1":
                list_all_audio_devices()

            elif choice == "2":
                detect_wifi_stream()

            elif choice == "3":
                device_index = input("\n  Digite o índice do dispositivo: ").strip()
                try:
                    device_index = int(device_index)
                    duration = input("  Duração da gravação (segundos, padrão=3): ").strip()
                    duration = int(duration) if duration else 3
                    test_audio_recording(device_index, duration)
                except ValueError:
                    print("  ❌ Índice inválido!")

            elif choice == "4":
                check_womic_status()

            elif choice == "5":
                # Complete workflow
                check_womic_status()
                device_index = detect_wifi_stream()

                if device_index is not None:
                    print("\n  Deseja testar a gravação deste dispositivo?")
                    test_choice = input("  (s/n): ").strip().lower()

                    if test_choice == 's':
                        test_audio_recording(device_index, duration=3)

            elif choice == "0":
                print("\n  👋 Até mais!\n")
                break

            else:
                print("\n  ❌ Opção inválida!")

            input("\n  Pressione ENTER para continuar...")

        except KeyboardInterrupt:
            print("\n\n  👋 Até mais!\n")
            break
        except Exception as e:
            print(f"\n  ❌ Erro: {e}")
            input("\n  Pressione ENTER para continuar...")


def main():
    """Main entry point."""
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║           🎤 BMO - Wi-Fi Audio Stream Detector 📡                  ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    # Check if running with arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "list":
            list_all_audio_devices()
        elif command == "detect":
            detect_wifi_stream()
        elif command == "test":
            if len(sys.argv) > 2:
                try:
                    device_index = int(sys.argv[2])
                    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 3
                    test_audio_recording(device_index, duration)
                except ValueError:
                    print("❌ Uso: detect_wifi_stream.py test <device_index> [duration]")
            else:
                print("❌ Uso: detect_wifi_stream.py test <device_index> [duration]")
        elif command == "status":
            check_womic_status()
        elif command == "auto":
            # Automatic workflow
            check_womic_status()
            device_index = detect_wifi_stream()
            if device_index is not None:
                test_audio_recording(device_index, duration=3)
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("\nComandos disponíveis:")
            print("  list    - Listar todos dispositivos")
            print("  detect  - Detectar dispositivo Wi-Fi")
            print("  test    - Testar gravação")
            print("  status  - Status do WO Mic")
            print("  auto    - Workflow completo")
    else:
        # Interactive mode
        interactive_menu()


if __name__ == "__main__":
    main()
