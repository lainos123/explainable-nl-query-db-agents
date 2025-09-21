#!/usr/bin/env python3
"""
create_embeddings.py

Create and save embeddings for the processed Spider schemas.

This script:
1. Loads the processed schema JSONL file
2. Creates embeddings using OpenAI's text-embedding-3-small model
3. Builds a FAISS vector store for efficient similarity search
4. Saves the vector store to disk for later use

Usage:
    python3 -m scripts.create_embeddings
"""

import sys
from pathlib import Path
from typing import List

# Import project config
from src.config import EMBEDDINGS_FOLDER, PROJECT_ROOT, SCHEMA_PROCESSED_FILE

# Add project root to Python path
sys.path.append(str(PROJECT_ROOT))

# Import LangChain components
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def load_processed_schema(input_file: Path) -> List[str]:
    """Load processed schema JSONL back into a list of strings."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(lines)} entries from {input_file}")
        return lines
    except FileNotFoundError:
        print(f"Error: Processed schema file '{input_file}' not found.")
        print("Please run 'python3 -m scripts.process_schemas' first.")
        return []
    except Exception as e:
        print(f"Error loading processed schema: {e}")
        return []


def create_and_save_embeddings(
    schema_texts: List[str], embeddings_folder: Path
) -> None:
    """Create embeddings and save FAISS vector store"""
    try:
        print("Creating embeddings...")
        embeddings = OpenAIEmbeddings()

        print("Building FAISS vector store...")
        vectorstore = FAISS.from_texts(schema_texts, embeddings)

        print("Saving vector store...")
        embeddings_folder.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(embeddings_folder))

        print(f"Saved schema embeddings to {embeddings_folder}")

    except Exception as e:
        print(f"Error creating embeddings: {e}")
        raise


def main():
    """Main embedding creation pipeline"""
    print("=" * 60)
    print("CREATING SCHEMA EMBEDDINGS")
    print("=" * 60)

    # Step 1: Load processed schema
    print("\n1. Loading processed schema...")
    schema_texts = load_processed_schema(SCHEMA_PROCESSED_FILE)

    if not schema_texts:
        print("No schema texts to process. Exiting.")
        return

    # Step 2: Create and save embeddings
    print("\n2. Creating and saving embeddings...")
    create_and_save_embeddings(schema_texts, EMBEDDINGS_FOLDER)

    print("\n" + "=" * 60)
    print("EMBEDDING CREATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
