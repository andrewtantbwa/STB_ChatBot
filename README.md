# STB ChatBot Prototype

This repository contains a Python prototype that connects a GPT-5 powered assistant with HeyGen's audio generation API. It demonstrates how to collect user prompts, forward them to OpenAI's GPT-5 model, and synthesize the assistant's replies into speech using HeyGen voices.

## Features

- Command line conversation loop with conversation history.
- GPT-5 text generation via OpenAI's Python SDK.
- HeyGen text-to-speech synthesis and polling for audio completion.
- Environment-based configuration with `.env` support.
- Modular Python package that can be reused in other applications.

## Requirements

- Python 3.10+
- OpenAI API key with access to the `gpt-5` model
- HeyGen API key with TTS permissions

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The runtime prototype depends on the optional packages `openai`, `python-dotenv`, and `requests`. They are listed in
`requirements.txt`; install them individually if you prefer not to use the bundled file. For local development and tests,
use the helper file:

```bash
pip install -r requirements-dev.txt
```

Optionally create a `.env` file in the project root:

```bash
OPENAI_API_KEY="sk-..."
OPENAI_API_BASE="https://api.openai.com/v1"  # optional custom endpoint
HEYGEN_API_KEY="hg-..."
HEYGEN_VOICE_ID="charles"  # Replace with a valid HeyGen voice ID
```

## Usage

Run the interactive prototype:

```bash
python -m stb_chatbot.main
```

The program starts a simple command line chat. Enter a blank line to exit. Each AI response is:

1. Printed to the console.
2. Converted to speech and saved as `output/audio_<timestamp>.mp3`.

You can change the audio output folder with the `--audio-dir` option:

```bash
python -m stb_chatbot.main --audio-dir my_audio
```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── stb_chatbot
│   ├── __init__.py
│   ├── audio.py
│   ├── chatbot.py
│   ├── config.py
│   ├── llm.py
│   └── main.py
└── tests
    └── test_config.py
```

## HeyGen API Notes

The `HeyGenClient` class in `stb_chatbot.audio` follows HeyGen's REST API contract:

1. Create a text-to-speech task via `POST /v1/tts`. The response either contains a `task_id` or raw audio data.
2. If a `task_id` is returned, poll `GET /v1/task-status/{task_id}` until the task completes, then download the audio from the provided URL.

Refer to HeyGen's [developer documentation](https://docs.heygen.com) for the latest endpoints, authentication rules, and available voices. Update the URLs in `HeyGenClient` if their API changes.

## Development

Run static checks:

```bash
python -m compileall stb_chatbot
pytest
```

The prototype uses standard Python logging; adjust the logging configuration in `stb_chatbot.main` for your environment.
