# Reka Chat Demo

This project demonstrates the capabilities of Reka AI alongside OpenAI's GPT model, creating a powerful hybrid chat experience.

## Features
- Dual AI responses from both Reka and OpenAI
- Rich console formatting for better readability
- Support for both interactive chat and command-line message input

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Add your API keys to the `.env` file:
- Get your Reka API key from https://docs.reka.ai/
- Get your OpenAI API key from https://platform.openai.com/

## Usage

Interactive mode:
```bash
python chat.py
```

Single message mode:
```bash
python chat.py "Your message here"
```

Type 'exit' or press Ctrl+C to quit the chat.