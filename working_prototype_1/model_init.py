import dspy
import outlines
import warnings

def initialize_llm(model_id: str = "hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4"):
    """Initialize LLM with proper warning handling"""
    # Suppress expected model initialization warnings
    warnings.filterwarnings("ignore", message="Some weights of the model checkpoint")
    
    try:
        dspy_model = dspy.HFModel(model=model_id, hf_device_map="cuda:0")
        dspy_model.drop_prompt_from_output = True
        
        return outlines.models.Transformers(
            model=dspy_model.model,
            tokenizer=dspy_model.tokenizer
        )
    except RuntimeError as e:
        if "CUDA" in str(e):
            print("CUDA device not available, falling back to CPU")
            dspy_model = dspy.HFModel(model=model_id, device="cpu")
            dspy_model.drop_prompt_from_output = True
            return outlines.models.Transformers(
                model=dspy_model.model,
                tokenizer=dspy_model.tokenizer
            )
        raise e 