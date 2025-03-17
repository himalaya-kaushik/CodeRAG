# CodeRAG

Welcome to **CodeRAG**, a repository dedicated to exploring and implementing Retrieval-Augmented Generation (RAG) techniques in code generation and understanding.

## Overview

This project aims to leverage the power of RAG to enhance code-related tasks, including but not limited to:

- **Code Generation**: Using RAG to generate code snippets or entire functions based on natural language queries.
- **Code Understanding**: Improving the comprehension of existing code by providing contextually relevant information or explanations.
- **Code Completion**: Assisting developers by suggesting code completions that are contextually accurate and useful.

## Repository Structure

- **chatbot_langchain.py**: Implements a chatbot using LangChain for conversational code assistance.
- **chromaDB.py**: Contains utilities for managing a ChromaDB, which is used for storing and retrieving code snippets or documentation.
- **chroma_sanity_check.py**: A script to verify the integrity and functionality of the ChromaDB setup.
- **langchain_try.py**: Experiments with LangChain for various code-related tasks.
- **parser.py**: A module for parsing code or natural language queries into a format suitable for RAG processing.
- **query_classifier.py**: Classifies queries to determine the appropriate RAG strategy or model to use.
- **summary_generator.py**: Generates summaries or explanations of code snippets or functions.

## Getting Started

To get started with CodeRAG:

1. **Clone the Repository**:
- git clone https://github.com/himalaya-kaushik/CodeRAG.git
- cd CodeRAG

2. **Setup Environment**:
- Ensure Python 3.8+ is installed.
- Install dependencies:
- Make sure you have ollama in you system and change your specific ollama model in chatbot_langchain.py file
  ```
  pip install -r requirements.txt
  ```

3. **Run Examples**:
- Run `python parser.py` where you put your github repo link in the repo_url.
- Run `python chromaDB.py` for store the embeddings in vector db .
- Try running `python chatbot_langchain.py` to interact with the chatbot.
- Use `python chroma_sanity_check.py` to ensure your ChromaDB is set up correctly.

## Usage

- **Chatbot**: Engage with the chatbot to get code suggestions or explanations. Use commands like `explain this code` or `write a function to...`.
- **Code Generation**: Use the provided scripts to generate code based on your requirements.
- **Code Understanding**: Query the system for explanations or summaries of code snippets.
