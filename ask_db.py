import numpy as np
import requests
import argparse
import json
import pickle
import time

# --- Configuration ---
OLLAMA_EMBED_URL = "http://1.0.0.127.0:11434/api/embeddings"  # Corrected URL for Ollama's embedding API
OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"  # URL for generating the final answer

def ask_question(db_name, question):
    """
    Loads the vector database, performs a semantic search for the user's question,
    sends the relevant context to Ollama to generate an answer, and prints performance metrics.
    """
    
    script_start_time = time.time()
    
    chunks_file = f"{db_name}.chunks"
    embeddings_file = f"{db_name}_embeddings.npy"

    # --- 1. Load the Knowledge Base Files ---
    print(f"Loading knowledge base: '{db_name}'...")
    try:
        db_embeddings = np.load(embeddings_file)
        with open(chunks_file, 'rb') as f:
            db_chunks = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: Database files for '{db_name}' not found. Please run create_db.py first.")
        return

    # --- Robustness Check: Ensure the database is not empty ---
    if db_embeddings.shape[0] == 0:
        print("Error: The vector database is empty. It seems no text chunks were indexed.")
        return

    load_db_end_time = time.time()
    print(f"Knowledge base loaded in {load_db_end_time - script_start_time:.2f} seconds.")

    # --- 2. Get Embedding for the User's Question from Ollama ---
    print("Embedding question...")
    try:
        embed_payload = {"model": "phi3", "prompt": question}
        response = requests.post(OLLAMA_EMBED_URL, json=embed_payload)
        response.raise_for_status()
        question_embedding = np.array(response.json()['embedding'])
    except Exception as e:
        print(f"Error getting embedding for the question: {e}"); return
        
    # --- 3. Perform Semantic Search with NumPy ---
    print("Performing semantic search...")
    # Calculate cosine similarity between the question and all document chunks
    similarities = np.dot(db_embeddings, question_embedding) / (np.linalg.norm(db_embeddings, axis=1) * np.linalg.norm(question_embedding))
    
    # Get the indices of the top 5 most relevant chunks
    top_k_indices = np.argsort(similarities)[-5:][::-1]

    # --- 4. Retrieve Context and Augment the Final Prompt ---
    retrieved_context = "\n---\n".join([db_chunks[i] for i in top_k_indices])
    
    final_prompt = f"""Based *only* on the CONTEXT provided below, please provide a comprehensive answer for the following QUESTION. If the answer is not in the CONTEXT, say 'The answer is not found in the provided context.'

QUESTION: \"{question}\"

CONTEXT:
\"\"\"
{retrieved_context}
\"\"\"
"""
    search_end_time = time.time()
    print(f"Context retrieved in {search_end_time - load_db_end_time:.2f} seconds.")
    print("Asking main LLM for the final answer...")
    
    # --- 5. Call Ollama's Generate API with Streaming ---
    generate_payload = {"model": "phi3", "prompt": final_prompt, "stream": True}
    
    full_response_content = ""
    metrics_data = None
    
    try:
        with requests.post(OLLAMA_GENERATE_URL, json=generate_payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        full_response_content += data['response']
                    if data.get('done', False):
                        metrics_data = data
                        
    except requests.exceptions.RequestException as e:
        print(f"\nError connecting to Ollama: {e}"); return
    except json.JSONDecodeError:
        print("\nError: Could not decode JSON response from Ollama."); return

    # --- 6. Print Formatted Answer ---
    print("\n----------------- ANSWER -----------------")
    print(full_response_content.strip())
    print("----------------------------------------")
    
    # --- 7. Calculate and Print Performance Metrics ---
    print("\n--------------- METRICS -----------------")
    if metrics_data:
        try:
            total_duration_ns = metrics_data.get('total_duration', 0)
            prompt_eval_count = metrics_data.get('prompt_eval_count', 0)
            prompt_eval_duration_ns = metrics_data.get('prompt_eval_duration', 0)
            eval_count = metrics_data.get('eval_count', 0)
            eval_duration_ns = metrics_data.get('eval_duration', 0)

            total_duration_s = total_duration_ns / 1_000_000_000
            prompt_eval_duration_s = prompt_eval_duration_ns / 1_000_000_000
            eval_duration_s = eval_duration_ns / 1_000_000_000
            
            prefill_tok_sec = prompt_eval_count / prompt_eval_duration_s if prompt_eval_duration_s > 0 else 0
            decode_tok_sec = (eval_count - 1) / eval_duration_s if eval_duration_s > 0 and eval_count > 1 else 0
            inter_token_latency_ms = (eval_duration_s / (eval_count - 1)) * 1000 if eval_duration_s > 0 and eval_count > 1 else 0
            pre_processing_time_s = search_end_time - script_start_time
            
            print(f"Doc Pre-processing Time     : {pre_processing_time_s:.3f} seconds")
            print(f"LLM Inference Time          : {total_duration_s:.3f} seconds")
            print(f"Time to First Token (TTFT)  : {prompt_eval_duration_s:.3f} seconds")
            print(f"Prefill Tokens              : {prompt_eval_count} tokens")
            print(f"Prefill Speed               : {prefill_tok_sec:.2f} tok/sec")
            print(f"Generated Tokens            : {eval_count} tokens")
            print(f"Decode Speed                : {decode_tok_sec:.2f} tok/sec")
            print(f"Inter-Token Latency (avg)   : {inter_token_latency_ms:.2f} ms")

        except Exception as e:
            print(f"Could not calculate metrics. Error: {e}")
    else:
        print("Metrics object not found in the Ollama response.")
        
    print("----------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask a question using a NumPy vector DB.")
    parser.add_argument("db_name", help="Base name of the database (e.g., 'master_db').")
    parser.add_argument("question", help="The question to ask, in quotes.")
    args = parser.parse_args()
    ask_question(args.db_name, args.question)