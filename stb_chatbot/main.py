"""Command line entry point for the chatbot prototype."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from .chatbot import ChatBot
from .config import Settings

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GPT-5 + HeyGen chatbot prototype")
    parser.add_argument(
        "--audio-dir",
        type=Path,
        help="Directory to write synthesized audio files to (overrides CHATBOT_AUDIO_DIR)",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()

    settings = Settings.load()
    if args.audio_dir:
        settings.audio_dir = args.audio_dir
        settings.ensure_output_dir()

    bot = ChatBot(settings)

    console.print("[bold green]STB ChatBot Prototype[/bold green]")
    console.print("Type your prompt and press enter. Submit an empty line to exit.\n")

    while True:
        user_input = Prompt.ask("You", default="", show_default=False)
        if not user_input.strip():
            console.print("Goodbye!")
            break

        response = bot.ask(user_input)
        console.print(f"[bold cyan]Assistant:[/bold cyan] {response}")

        audio_path = bot.speak(response)
        if audio_path:
            console.print(f"[green]Audio saved to:[/green] {audio_path}")
        else:
            console.print("[yellow]Audio synthesis skipped.[/yellow]")


if __name__ == "__main__":
    main()
