# come back here, but after some time maybe we here will define things such as , which agent, how long, steps, etc, like configure it, and talk to our game..
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Callable, Optional, List, Dict, Tuple # remove List, Dict, Tuple we are on newer 3.9+ brahok

import typer
from rich.console import Console
from rich.table import Table

console = Console()
GAMES_DIR = Path(__file__).parent / "games"


def _pretty(stem: str) -> str:
    return " ".join(p.capitalize() for p in stem.replace("-", "_").split("_"))


def discover_games() -> List[Dict[str, str]]:
    """
    Find games in ./games as python modules.
    Returns a list of dicts: [{"id": "game-1", "name": "Game 1", "module": "games.game_1"}]
    """
    items: List[Dict[str, str]] = []
    if not GAMES_DIR.exists():
        return items

    for file in sorted(GAMES_DIR.glob("*.py")):
        if file.name.startswith("_") or file.name == "__init__.py":
            continue

        stem = file.stem
        module_name = f"games.{stem}"

        try:
            mod = importlib.import_module(module_name)
        except Exception as e:
            console.print(f"[yellow]Skipping {file.name} (import failed): {e}[/]")
            continue

        game_id = getattr(mod, "GAME_ID", stem.replace("_", "-"))
        game_name = getattr(mod, "GAME_NAME", _pretty(stem))

        items.append({"id": str(game_id), "name": str(game_name), "module": module_name})

    return items


def get_runner(module_name: str) -> Optional[Callable[[], None]]:
    """
    Prefer start() -> main_loop() -> main() each time we run (supports edits).
    """
    try:
        mod = importlib.import_module(module_name)
        mod = importlib.reload(mod)  # pick up code changes between runs
    except Exception as e:
        console.print(f"[red]Failed to import {module_name}: {e}[/]")
        return None

    return getattr(mod, "start", None) or getattr(mod, "main_loop", None) or getattr(mod, "main", None)


def show_menu(items: List[Dict[str, str]]) -> None:
    table = Table(title="Available Games")
    table.add_column("#/ID", justify="left", no_wrap=True)
    table.add_column("Name", justify="left")

    table.add_row("0", "Quit")
    for idx, it in enumerate(items, start=1):
        table.add_row(str(idx), f"{it['name']}  [dim]({it['id']})[/]")

    console.print(table)


def pick(items: List[Dict[str, str]], last_choice: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Prompt until the user picks a valid number/id or 0 to quit.
    Allows pressing Enter to repeat the last choice.
    """
    prompt_text = "Select game by number or id (0=quit)"
    if last_choice:
        prompt_text += f" [{last_choice}]"

    while True:
        try:
            raw = typer.prompt(prompt_text, default=last_choice or "")
        except typer.Abort:
            # Ctrl+C on the prompt
            return None

        s = str(raw).strip()
        if s == "" and last_choice:  # repeat last
            s = last_choice

        if s == "0":
            return None

        # number?
        if s.isdigit():
            n = int(s)
            if 1 <= n <= len(items):
                return items[n - 1]
            console.print(f"[red]Pick a number between 0 and {len(items)}[/]")
            continue

        # try id match (case-insensitive)
        for it in items:
            if s.lower() == it["id"].lower():
                return it

        console.print(f"[red]Unknown selection:[/] {s}. Enter a number or an id shown in the table.")


def main():
    last_choice: Optional[str] = None

    while True:
        items = discover_games()
        if not items:
            console.print("[red]No games found in ./games[/]")
            raise typer.Exit(1)

        show_menu(items)
        selection = pick(items, last_choice)

        if selection is None:
            console.print("[green]Bye![/]")
            break

        last_choice = selection["id"]
        runner = get_runner(selection["module"])
        if runner is None or not callable(runner):
            console.print(
                f"[red]'{selection['name']}' has no start()/main_loop()/main(). Skipping.[/]"
            )
            continue

        console.rule(f"[bold]Starting {selection['name']}[/] ({selection['id']})")

        try:
            runner()
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Returning to menu...[/]")
        except SystemExit:
            # allow games to call sys.exit cleanly
            pass
        except Exception as e:
            console.print(f"[red]Game crashed:[/] {e}")
        finally:
            console.print("[blue]Returning to menu...[/]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[green]Bye![/]")
