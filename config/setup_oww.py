# setup_oww.py (Versão 2.0 - Caminho Explícito)
# Script para verificar e baixar os modelos base necessários para o OpenWakeWord.

import os
import urllib.request
import sys

print("🔧 Preparando ambiente para OpenWakeWord...")

import sysconfig
site_packages = sysconfig.get_paths()["purelib"]
TARGET_DIR = os.path.join(site_packages, "openwakeword", "resources", "models")

# Dicionário de modelos essenciais e seus URLs
MODELS_TO_DOWNLOAD = {
    "melspectrogram.onnx": "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx",
    "embedding_model.onnx": "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx"
}

def download_model(model_name, url):
    """Baixa um único modelo se ele não existir."""
    destination_path = os.path.join(TARGET_DIR, model_name)
    if not os.path.exists(destination_path):
        print(f"   Baixando '{model_name}'...")
        try:
            # Adiciona um User-Agent para evitar bloqueios HTTP 403
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, destination_path)
            print(f"   ✅ '{model_name}' baixado com sucesso.")
        except Exception as e:
            print(f"   ❌ ERRO ao baixar '{model_name}': {e}")
    else:
        print(f"   ✅ '{model_name}' já existe.")

if __name__ == "__main__":
    print(f"Verificando modelos base em: '{TARGET_DIR}'")
    
    if not os.path.exists(TARGET_DIR):
        print("   Criando diretório de modelos...")
        os.makedirs(TARGET_DIR)

    for name, url in MODELS_TO_DOWNLOAD.items():
        download_model(name, url)

    print("\nVerificação concluída. O ambiente está pronto para o OpenWakeWord.")