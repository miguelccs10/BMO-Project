"""
AirLLM LangChain Wrapper
Allows using AirLLM with LangChain for low-VRAM inference (CPU/GPU).
"""

from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from pydantic import PrivateAttr
import torch

class AirLLMWrapper(LLM):
    """LangChain LLM wrapper for AirLLM."""
    
    hf_repo: str
    compression: Optional[str] = None
    max_length: int = 512
    max_new_tokens: int = 150
    
    _model: Any = PrivateAttr()
    _device: Any = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from airllm import AutoModel
        print(f"⏳ Inicializando AirLLM com repositório '{self.hf_repo}'...")
        
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if self.compression:
            print(f"   Usando compressão: {self.compression}")
            self._model = AutoModel.from_pretrained(self.hf_repo, compression=self.compression, device=self._device)
        else:
            self._model = AutoModel.from_pretrained(self.hf_repo, device=self._device)
        print(f"✅ AirLLM carregado com sucesso. Device inferido: {self._device}")
        
    @property
    def _llm_type(self) -> str:
        return "airllm"
        
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given prompt."""
        
        # Tokenize input
        input_tokens = self._model.tokenizer(
            [prompt], 
            return_tensors="pt", 
            return_attention_mask=True, 
            truncation=True, 
            max_length=self.max_length, 
            padding=False
        )
        
        # Move to correct device
        input_ids = input_tokens['input_ids']
        attention_mask = input_tokens['attention_mask']
        
        if self._device == "cuda":
            input_ids = input_ids.cuda()
            attention_mask = attention_mask.cuda()
            
        # Generate
        generation_output = self._model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=self.max_new_tokens,
            use_cache=True, 
            return_dict_in_generate=True
        )
        
        # Decode only the generated response (not the prompt)
        generated_sequence = generation_output.sequences[0]
        input_len = len(input_ids[0])
        new_tokens = generated_sequence[input_len:]
        
        output = self._model.tokenizer.decode(
            new_tokens,
            skip_special_tokens=True
        )
        
        return output.strip()
