import os
import sys
import yaml
import argparse

OLLAMA_MODELS = {
    "small": "qwen2:1.5b",
    "medium": "llama3.1:8b",
    "large": "gemma2:27b"
}

AIRLLM_MODELS = {
    "small": "Qwen/Qwen1.5-1.8B-Chat",
    "medium": "Qwen/Qwen1.5-7B-Chat",
    "large": "Qwen/Qwen1.5-14B-Chat"
}

STT_MODELS = {
    "small": "small",
    "medium": "medium",
    "large": "large-v3"
}

def update_config(provider, weight):
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    
    if not os.path.exists(config_path):
        print(f"Erro: Arquivo {config_path} não encontrado.")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    if provider == "ollama":
        config["llm"]["local"]["provider"] = "ollama"
        config["llm"]["local"]["model"] = OLLAMA_MODELS[weight]
        print(f"✅ LLM configurado para Ollama ({OLLAMA_MODELS[weight]})")
    elif provider == "airllm":
        config["llm"]["local"]["provider"] = "airllm"
        if "airllm" not in config["llm"]["local"]:
            config["llm"]["local"]["airllm"] = {"compression": None, "max_length": 128}
        config["llm"]["local"]["airllm"]["hf_repo"] = AIRLLM_MODELS[weight]
        print(f"✅ LLM configurado para AirLLM ({AIRLLM_MODELS[weight]})")
        
    config["stt"]["local"]["model"] = STT_MODELS[weight]
    print(f"✅ STT configurado para faster-whisper ({STT_MODELS[weight]})")
    
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
    print("✨ config.yaml atualizado com sucesso!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BMO Configurator")
    parser.add_argument("--provider", choices=["ollama", "airllm"], required=True)
    parser.add_argument("--weight", choices=["small", "medium", "large"], required=True)
    args = parser.parse_args()
    
    update_config(args.provider, args.weight)
