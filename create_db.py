import os
import numpy as np
import requests
import json
import subprocess
import argparse
import time
import pickle
from pypdf import PdfReader

OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embeddings"

def extract_text_from_pptx(pptx_path):
    """Uses pandoc to extract text from a PPTX file."""
    try:
        result = subprocess.run(['pandoc', '-t', 'plain', pptx_path], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        print(f"  - Warning: Pandoc failed on {os.path.basename(pptx_path)}. Skipping. Error: {e}")
        return ""

def get_embedding(text_chunk):
    """Gets a single embedding from the Ollama API."""
    try:
        payload = {"model": "phi3", "prompt": text_chunk}
        response = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=60) # 60-second timeout
        response.raise_for_status()
        return response.json().get('embedding')
    except requests.exceptions.RequestException as e:
        print(f"\nAPI Error: {e}. Retrying once...")
        time.sleep(2) # Wait 2 seconds before retrying
        try:
            response = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get('embedding')
        except Exception as retry_e:
            print(f"Retry failed: {retry_e}")
            return None
    except Exception as e:
        print(f"\nAn unexpected error occurred during embedding: {e}")
        return None

def create_database(input_path, db_name):
    """Processes a file or a directory of 1000+ files into a robust vector DB."""
    
    source_files = []
    if os.path.isdir(input_path):
        print(f"Scanning directory for PDF and PPTX files: {input_path}")
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(('.pdf', '.pptx')):
                    source_files.append(os.path.join(root, file))
    elif os.path.isfile(input_path):
        if input_path.lower().endswith(('.pdf', '.pptx')):
            source_files.append(input_path)
    else:
        print(f"Error: Path '{input_path}' is not a valid file or directory.")
        return

    if not source_files:
        print(f"Error: No supported files found in '{input_path}'."); return

    print(f"Found {len(source_files)} document(s) to process.")
    
    all_chunks = []
    all_embeddings = []

    for i, file_path in enumerate(source_files):
        print(f"\n[{i+1}/{len(source_files)}] Processing: {os.path.basename(file_path)}...")
        
        full_text = ""
        if file_path.lower().endswith('.pdf'):
            try:
                reader = PdfReader(file_path)
                full_text = "".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                print(f"  - Warning: Skipping corrupted PDF. Error: {e}"); continue
        elif file_path.lower().endswith('.pptx'):
            full_text = extract_text_from_pptx(file_path)

        if not full_text.strip():
            print("  - Warning: No text extracted."); continue

        file_chunks = [p.strip() for p in full_text.split('\n') if len(p.strip()) > 50]
        print(f"  - Found {len(file_chunks)} chunks. Generating embeddings...", end="", flush=True)

        for j, chunk in enumerate(file_chunks):
            embedding = get_embedding(chunk)
            if embedding:
                all_chunks.append(chunk)
                all_embeddings.append(embedding)
                # Corrected progress indicator line
                print(".", end="", flush=True)
            else:
                # Added a newline for better formatting after a failure
                print(f"\n  - Warning: Failed to get embedding for a chunk. Skipping.")
        
        print(f"\n  - Finished processing {os.path.basename(file_path)}.")

    if not all_chunks:
        print("Error: Failed to create any chunks/embeddings from the dataset."); return
    
    print(f"\nTotal chunks indexed: {len(all_chunks)}")
    
    embeddings_filename = f"{db_name}_embeddings.npy"
    chunks_filename = f"{db_name}.chunks"
    
    print(f"Saving database files...")
    np.save(embeddings_filename, np.array(all_embeddings))
    with open(chunks_filename, "wb") as f:
        pickle.dump(all_chunks, f)
        
    print(f"\nSuccessfully created database '{db_name}'!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a NumPy vector DB from a file or directory.")
    parser.add_argument("input_path", help="Path to the PDF/PPTX file or a directory.")
    parser.add_argument("--name", default="master_db", help="The base name for your DB files.")
    args = parser.parse_args()
    create_database(args.input_path, args.name)