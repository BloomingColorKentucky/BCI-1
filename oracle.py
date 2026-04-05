#!/usr/bin/env python3
"""
The Yes/No Oracle — asks Claude any question and receives a truthful yes or no answer.
"""

import os
import sys
import time
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.prompt import Prompt
from rich import box
from rich.live import Live
from rich.spinner import Spinner

console = Console()

BANNER = r"""
 __   __ ___  ____       _  _  ___     ___  ____   __    ___  __    ____
 \ \ / // __)/  _/      | \| |/ _ \   / _ \| _ \  /__\  / __|| |   | __|
  \ V /| _|  _\ \  ___  | .  | (_) | | (_) |   / / \/ \| (__ | |_  | _|
   |_/ |___||___/ |___| |_|\_|\___/   \___/|_|_\ \__/\__/\___||___||___|
"""

BANNER_COMPACT = "✦  THE YES/NO ORACLE  ✦"

YES_ART = r"""
██╗   ██╗███████╗███████╗
╚██╗ ██╔╝██╔════╝██╔════╝
 ╚████╔╝ █████╗  ███████╗
  ╚██╔╝  ██╔══╝  ╚════██║
   ██║   ███████╗███████║
   ╚═╝   ╚══════╝╚══════╝"""

NO_ART = r"""
███╗   ██╗ ██████╗
████╗  ██║██╔═══██╗
██╔██╗ ██║██║   ██║
██║╚██╗██║██║   ██║
██║ ╚████║╚██████╔╝
╚═╝  ╚═══╝ ╚═════╝ """

DIVIDER_CHAR = "─"


def clear():
    console.clear()


def draw_header():
    console.print()
    header = Text(BANNER_COMPACT, style="bold bright_magenta", justify="center")
    console.print(Align.center(header))
    subtitle = Text("Truthful answers. Nothing more.", style="italic dim", justify="center")
    console.print(Align.center(subtitle))
    console.print()
    console.print(Rule(style="bright_magenta dim"))
    console.print()


def draw_footer():
    console.print()
    console.print(Rule(style="bright_magenta dim"))
    footer = Text('Type "exit" or "quit" to leave  ·  Any question answered honestly',
                  style="dim", justify="center")
    console.print(Align.center(footer))
    console.print()


def ask_claude(question: str) -> str:
    """Ask Claude to answer yes or no, truthfully."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    system_prompt = (
        "You are the Yes/No Oracle. You answer every question with ONLY one of two possible words: "
        "YES or NO. Nothing else. No punctuation, no explanation, no hedging. "
        "You always answer truthfully and to the best of your knowledge. "
        "If a question is ambiguous, answer based on the most reasonable interpretation. "
        "If a question has no meaningful yes/no answer (e.g., nonsense), respond with NO. "
        "Your entire response must be exactly one word: either YES or NO."
    )

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=10,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )

    answer = response.content[0].text.strip().upper()
    # Normalize — only accept YES or NO
    if "YES" in answer:
        return "YES"
    elif "NO" in answer:
        return "NO"
    else:
        return "NO"


def animate_thinking():
    """Show a thinking animation while Claude processes."""
    with Live(
        Align.center(
            Panel(
                Align.center(Spinner("dots2", text=" Consulting the oracle...", style="bold bright_magenta")),
                border_style="bright_magenta dim",
                box=box.ROUNDED,
                width=50,
                padding=(1, 4),
            )
        ),
        console=console,
        refresh_per_second=12,
    ) as live:
        return live


def display_answer(question: str, answer: str):
    """Render the answer with fanfare."""
    clear()
    draw_header()

    # Show the question
    q_text = Text(f'"{question}"', style="italic white", justify="center")
    console.print(Align.center(q_text))
    console.print()
    console.print(Align.center(Text("The oracle speaks:", style="dim")))
    console.print()

    if answer == "YES":
        art = Text(YES_ART, style="bold bright_green", justify="center")
        panel_style = "bright_green"
        glow_char = "✓"
        msg = Text(f"  {glow_char}  YES  {glow_char}  ", style="bold bright_green on green")
    else:
        art = Text(NO_ART, style="bold bright_red", justify="center")
        panel_style = "bright_red"
        glow_char = "✗"
        msg = Text(f"  {glow_char}  NO  {glow_char}  ", style="bold bright_red on red")

    console.print(
        Align.center(
            Panel(
                Align.center(art),
                border_style=panel_style,
                box=box.DOUBLE,
                padding=(1, 6),
                expand=False,
            )
        )
    )

    draw_footer()


def run():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(
            Panel(
                "[bold red]ANTHROPIC_API_KEY is not set.[/bold red]\n"
                "Export your key: [bold]export ANTHROPIC_API_KEY=your-key-here[/bold]",
                title="[red]Configuration Error[/red]",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        sys.exit(1)

    clear()
    draw_header()

    # Intro panel
    intro = Text.assemble(
        ("Ask me anything.\n", "bold white"),
        ("I will answer only with ", "dim"),
        ("YES", "bold bright_green"),
        (" or ", "dim"),
        ("NO", "bold bright_red"),
        (".\n\n", "dim"),
        ("Every answer is truthful.", "italic white"),
    )
    console.print(
        Align.center(
            Panel(
                Align.center(intro),
                border_style="bright_magenta",
                box=box.ROUNDED,
                padding=(1, 8),
                expand=False,
            )
        )
    )
    console.print()
    draw_footer()

    while True:
        try:
            console.print(Align.center(Text("─" * 60, style="dim")))
            question = Prompt.ask(
                "\n  [bold bright_magenta]❯[/bold bright_magenta] [bold white]Your question[/bold white]"
            )

            if not question.strip():
                continue

            if question.strip().lower() in ("exit", "quit", "q", "bye"):
                clear()
                draw_header()
                farewell = Text("The oracle has spoken its last word.\nFarewell.",
                                style="bold bright_magenta", justify="center")
                console.print(Align.center(farewell))
                console.print()
                draw_footer()
                break

            # Show thinking animation while calling API
            clear()
            draw_header()
            q_text = Text(f'"{question.strip()}"', style="italic white", justify="center")
            console.print(Align.center(q_text))
            console.print()

            with console.status(
                "[bold bright_magenta]Consulting the oracle...[/bold bright_magenta]",
                spinner="dots2",
                spinner_style="bright_magenta",
            ):
                answer = ask_claude(question.strip())

            display_answer(question.strip(), answer)

        except KeyboardInterrupt:
            clear()
            draw_header()
            farewell = Text("The oracle departs in silence.", style="italic dim", justify="center")
            console.print(Align.center(farewell))
            console.print()
            draw_footer()
            break
        except anthropic.APIError as e:
            console.print(
                Panel(
                    f"[red]API Error:[/red] {e}",
                    border_style="red",
                    box=box.ROUNDED,
                )
            )


if __name__ == "__main__":
    run()
