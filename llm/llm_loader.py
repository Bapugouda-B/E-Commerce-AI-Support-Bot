from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from config.settings import LLM_MODEL

def load_llm():
    pipe = pipeline(
        "text2text-generation",
        model=LLM_MODEL,
        max_new_tokens=256,     
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.1,  # avoid repeating short phrases
        num_beams=2,             # beam search for better answers
        min_length=20,           # <‑‑ force at least ~2–3 sentences
        no_repeat_ngram_size=3   # avoid “My Orders My Orders”
    )
    return HuggingFacePipeline(pipeline=pipe)
