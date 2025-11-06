#!/usr/bin/env python3
"""
BMO Wi-Fi Audio Setup Validator
Verifica se tudo está configurado corretamente para usar entrada de áudio Wi-Fi
"""

import sys
from pathlib import Path

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_header(text):
    """Print formatted header."""
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}  {text}{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")


def check_imports():
    """Check if all required modules can be imported."""
    print_header("🔍 Verificando Imports")

    errors = []

    # Test config_manager
    try:
        from config.config_manager import get_config
        print(f"{GREEN}✅ config.config_manager{NC}")
    except Exception as e:
        print(f"{RED}❌ config.config_manager: {e}{NC}")
        errors.append("config_manager")

    # Test wifi_audio_stream
    try:
        from bmo_core.services.wifi_audio_stream import WiFiAudioStreamManager
        print(f"{GREEN}✅ bmo_core.services.wifi_audio_stream{NC}")
    except Exception as e:
        print(f"{RED}❌ bmo_core.services.wifi_audio_stream: {e}{NC}")
        errors.append("wifi_audio_stream")

    # Test audio_manager
    try:
        from bmo_core.services.audio_manager import AudioManager
        print(f"{GREEN}✅ bmo_core.services.audio_manager{NC}")
    except Exception as e:
        print(f"{RED}❌ bmo_core.services.audio_manager: {e}{NC}")
        errors.append("audio_manager")

    return len(errors) == 0, errors


def check_config():
    """Check if configuration is valid."""
    print_header("⚙️ Verificando Configuração")

    try:
        from config.config_manager import get_config

        config = get_config()
        print(f"{GREEN}✅ Configuração carregada{NC}")
        print(f"   Versão: {config.BMO_VERSION}")
        print(f"   Usuário: {config.USER_NAME}")
        print(f"   LLM Mode: {config.config.llm.mode}")
        print(f"   STT Mode: {config.config.stt.mode}")
        print(f"   TTS Engine: {config.config.tts.engine}")

        # Check wifi_stream config
        if hasattr(config.config.recording, 'wifi_stream') and config.config.recording.wifi_stream:
            wifi_config = config.config.recording.wifi_stream
            print(f"\n{GREEN}✅ Configuração Wi-Fi Stream encontrada{NC}")
            print(f"   Enabled: {wifi_config.enabled}")
            print(f"   Auto-detect: {wifi_config.auto_detect}")
            print(f"   Fallback: {wifi_config.fallback_to_local}")

            if not wifi_config.enabled:
                print(f"\n{YELLOW}⚠️  Wi-Fi streaming está DESABILITADO{NC}")
                print(f"   Para habilitar, use: cp config/config.jetson_medium.yaml config/config.yaml")
                return False, "wifi_disabled"
        else:
            print(f"\n{YELLOW}⚠️  Configuração Wi-Fi Stream não encontrada{NC}")
            print(f"   Você está usando config antigo sem suporte a Wi-Fi")
            print(f"   Para habilitar, use: cp config/config.jetson_medium.yaml config/config.yaml")
            return False, "no_wifi_config"

        return True, None

    except Exception as e:
        print(f"{RED}❌ Erro ao carregar configuração: {e}{NC}")
        return False, str(e)


def check_files():
    """Check if all required files exist."""
    print_header("📁 Verificando Arquivos")

    base_dir = Path(__file__).parent.parent  # Go up to project root

    files_to_check = [
        ("bmo_core/services/wifi_audio_stream.py", "Wi-Fi Stream Manager"),
        ("tutorials/detect_wifi_stream.py", "Utilitário de Detecção"),
        ("tutorials/validate_wifi_setup.py", "Script de Validação"),
        ("requirements/setup_wifi_audio.sh", "Script de Instalação"),
        ("config/config.jetson_medium.yaml", "Config Jetson Medium"),
        ("docs/WIFI_AUDIO_SETUP.md", "Documentação Wi-Fi"),
        ("docs/QUICKSTART_WIFI_AUDIO.md", "Guia Rápido"),
        ("docs/IMPLEMENTACAO_COMPLETA.md", "Documentação Técnica"),
        ("docs/README_WIFI_AUDIO.md", "README Wi-Fi Audio"),
    ]

    all_exist = True

    for file_path, description in files_to_check:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"{GREEN}✅ {description}{NC}")
            print(f"   {file_path}")
        else:
            print(f"{RED}❌ {description} NÃO ENCONTRADO{NC}")
            print(f"   {file_path}")
            all_exist = False

    return all_exist


def check_permissions():
    """Check if scripts have execute permissions."""
    print_header("🔐 Verificando Permissões")

    base_dir = Path(__file__).parent.parent  # Go up to project root

    scripts = [
        "requirements/setup_wifi_audio.sh",
        "tutorials/detect_wifi_stream.py",
        "tutorials/validate_wifi_setup.py",
    ]

    all_ok = True

    for script in scripts:
        script_path = base_dir / script
        if script_path.exists():
            import os
            if os.access(script_path, os.X_OK):
                print(f"{GREEN}✅ {script} (executável){NC}")
            else:
                print(f"{YELLOW}⚠️  {script} (não executável){NC}")
                print(f"   Execute: chmod +x {script}")
                all_ok = False
        else:
            print(f"{RED}❌ {script} não encontrado{NC}")
            all_ok = False

    return all_ok


def check_dependencies():
    """Check if system dependencies are available."""
    print_header("📦 Verificando Dependências do Sistema")

    import subprocess

    commands = [
        ("python3", "Python 3"),
        ("pip3", "pip3"),
        ("pactl", "PulseAudio"),
        ("nmcli", "NetworkManager"),
    ]

    all_ok = True

    for cmd, description in commands:
        try:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                path = result.stdout.decode().strip()
                print(f"{GREEN}✅ {description} ({cmd}){NC}")
                print(f"   {path}")
            else:
                print(f"{YELLOW}⚠️  {description} não encontrado{NC}")
                all_ok = False
        except Exception as e:
            print(f"{RED}❌ Erro ao verificar {description}: {e}{NC}")
            all_ok = False

    # Check WO Mic (optional)
    try:
        result = subprocess.run(
            ["which", "womic"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            print(f"{GREEN}✅ WO Mic client instalado{NC}")
        else:
            print(f"{YELLOW}⚠️  WO Mic client não instalado (ainda){NC}")
            print(f"   Instale com: bash requirements/setup_wifi_audio.sh")
    except:
        pass

    return all_ok


def main():
    """Main validation routine."""
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║                                                                    ║{NC}")
    print(f"{BLUE}║         🎤 BMO Wi-Fi Audio Setup Validator 📡                      ║{NC}")
    print(f"{BLUE}║                                                                    ║{NC}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════════╝{NC}")

    results = {}

    # Run checks
    results['files'] = check_files()
    results['permissions'] = check_permissions()
    results['dependencies'] = check_dependencies()
    results['imports'], import_errors = check_imports()
    results['config'], config_issue = check_config()

    # Summary
    print_header("📊 Resumo da Validação")

    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)

    for check, passed in results.items():
        status = f"{GREEN}✅ PASSOU{NC}" if passed else f"{RED}❌ FALHOU{NC}"
        print(f"  {check.upper()}: {status}")

    print(f"\n{BLUE}{'─'*70}{NC}")
    print(f"  Total: {passed_checks}/{total_checks} checks passaram")
    print(f"{BLUE}{'─'*70}{NC}\n")

    # Recommendations
    if passed_checks == total_checks:
        print(f"{GREEN}🎉 TUDO OK! Sistema pronto para uso com Wi-Fi audio!{NC}\n")
        print(f"{BLUE}Próximos passos:{NC}")
        print(f"  1. Instalar WO Mic na Jetson: bash requirements/setup_wifi_audio.sh")
        print(f"  2. Copiar config: cp config/config.jetson_medium.yaml config/config.yaml")
        print(f"  3. Iniciar BMO: python app/BMO.py")
        print(f"\n  📚 Ver guia completo: docs/QUICKSTART_WIFI_AUDIO.md\n")
        return 0
    else:
        print(f"{YELLOW}⚠️  Alguns problemas foram encontrados. Veja acima para detalhes.{NC}\n")

        if not results['imports']:
            print(f"{RED}CRITICAL: Erros de importação encontrados!{NC}")
            print(f"  Ative o ambiente virtual: source venv/bin/activate")
            print(f"  Ou instale dependências: pip install -r requirements/x86_64.txt\n")

        if config_issue == "wifi_disabled":
            print(f"{YELLOW}INFO: Wi-Fi streaming está desabilitado na config atual{NC}")
            print(f"  Use: cp config/config.jetson_medium.yaml config/config.yaml\n")

        elif config_issue == "no_wifi_config":
            print(f"{YELLOW}INFO: Config atual não tem suporte a Wi-Fi streaming{NC}")
            print(f"  Use: cp config/config.jetson_medium.yaml config/config.yaml\n")

        return 1


if __name__ == "__main__":
    sys.exit(main())
