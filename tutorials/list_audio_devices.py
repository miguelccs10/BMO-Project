#!/usr/bin/env python3
"""
list_audio_devices.py
Lista todos os dispositivos de áudio disponíveis no sistema.
Use este script para descobrir os índices dos dispositivos para configurar no config.yaml.

Uso:
    python list_audio_devices.py
"""

import sys
import pyaudio

def list_audio_devices():
    """Lista todos os dispositivos de áudio disponíveis."""
    print("\n" + "="*70)
    print("🎧 DISPOSITIVOS DE ÁUDIO DISPONÍVEIS")
    print("="*70 + "\n")

    pa = pyaudio.PyAudio()

    # Get default devices
    try:
        default_input = pa.get_default_input_device_info()
        default_input_index = default_input['index']
    except IOError:
        default_input_index = None

    try:
        default_output = pa.get_default_output_device_info()
        default_output_index = default_output['index']
    except IOError:
        default_output_index = None

    # List all devices
    device_count = pa.get_device_count()

    input_devices = []
    output_devices = []

    for i in range(device_count):
        try:
            info = pa.get_device_info_by_index(i)

            # Determine device type
            is_input = info['maxInputChannels'] > 0
            is_output = info['maxOutputChannels'] > 0

            device_info = {
                'index': i,
                'name': info['name'],
                'channels_in': info['maxInputChannels'],
                'channels_out': info['maxOutputChannels'],
                'sample_rate': int(info['defaultSampleRate']),
                'is_default_input': i == default_input_index,
                'is_default_output': i == default_output_index
            }

            if is_input:
                input_devices.append(device_info)
            if is_output:
                output_devices.append(device_info)

        except Exception as e:
            print(f"⚠️  Erro ao ler dispositivo {i}: {e}")

    # Print input devices
    print("📥 DISPOSITIVOS DE ENTRADA (Microfones):")
    print("-" * 70)

    if not input_devices:
        print("   ❌ Nenhum dispositivo de entrada encontrado!")
    else:
        for dev in input_devices:
            default_marker = " [PADRÃO]" if dev['is_default_input'] else ""
            print(f"\n   Índice: {dev['index']}{default_marker}")
            print(f"   Nome: {dev['name']}")
            print(f"   Canais: {dev['channels_in']}")
            print(f"   Taxa de amostragem: {dev['sample_rate']} Hz")

    print("\n" + "="*70 + "\n")

    # Print output devices
    print("📤 DISPOSITIVOS DE SAÍDA (Alto-falantes/Fones):")
    print("-" * 70)

    if not output_devices:
        print("   ❌ Nenhum dispositivo de saída encontrado!")
    else:
        for dev in output_devices:
            default_marker = " [PADRÃO]" if dev['is_default_output'] else ""
            print(f"\n   Índice: {dev['index']}{default_marker}")
            print(f"   Nome: {dev['name']}")
            print(f"   Canais: {dev['channels_out']}")
            print(f"   Taxa de amostragem: {dev['sample_rate']} Hz")

    print("\n" + "="*70 + "\n")

    # Configuration instructions
    print("📝 COMO CONFIGURAR:")
    print("-" * 70)
    print("\n1. Identifique os índices dos dispositivos que deseja usar acima.")
    print("\n2. Edite config/config.yaml:")
    print("\n   recording:")
    print("     input_device_index: X   # ← Substitua X pelo índice do microfone")
    print("     output_device_index: Y  # ← Substitua Y pelo índice da saída")
    print("\n3. Use 'null' para usar os dispositivos padrão do sistema:")
    print("\n   recording:")
    print("     input_device_index: null")
    print("     output_device_index: null")
    print("\n" + "="*70 + "\n")

    # Jetson-specific tips
    print("💡 DICAS PARA JETSON ORIN:")
    print("-" * 70)
    print("\n• USB Audio: Geralmente aparecem como 'USB Audio Device'")
    print("• HDMI Audio: Pode aparecer como 'tegra-snd-xxx' ou 'HDMI'")
    print("• Jack 3.5mm: Geralmente é 'tegra-snd-t194xxx' ou similar")
    print("\n• Se não aparecer nenhum dispositivo USB:")
    print("  1. Conecte o dispositivo USB")
    print("  2. Execute: lsusb")
    print("  3. Reinicie o sistema se necessário")
    print("\n• Para testar um dispositivo:")
    print("  arecord -D hw:0,0 -f cd -d 5 test.wav  # Gravar 5 segundos")
    print("  aplay test.wav  # Reproduzir")
    print("\n" + "="*70 + "\n")

    pa.terminate()


def test_device(device_index, is_input=True):
    """Testa um dispositivo específico."""
    pa = pyaudio.PyAudio()

    try:
        if is_input:
            print(f"\n🎤 Testando dispositivo de entrada {device_index}...")
            stream = pa.open(
                rate=16000,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            print("   ✅ Dispositivo de entrada OK!")
        else:
            print(f"\n🔊 Testando dispositivo de saída {device_index}...")
            stream = pa.open(
                rate=16000,
                channels=1,
                format=pyaudio.paInt16,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=1024
            )
            print("   ✅ Dispositivo de saída OK!")

        stream.close()
        return True

    except Exception as e:
        print(f"   ❌ Erro ao testar dispositivo: {e}")
        return False
    finally:
        pa.terminate()


if __name__ == "__main__":
    # Check if testing a specific device
    if len(sys.argv) > 1:
        try:
            device_index = int(sys.argv[1])
            device_type = sys.argv[2] if len(sys.argv) > 2 else "input"
            is_input = device_type.lower() in ["input", "in", "i"]

            test_device(device_index, is_input)
        except ValueError:
            print("❌ Uso: python list_audio_devices.py [device_index] [input|output]")
            sys.exit(1)
    else:
        list_audio_devices()
