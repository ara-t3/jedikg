from __future__ import annotations

from pyfiglet import figlet_format
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import questionary
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.rule import Rule
from rich.progress import track
from rich.table import Table
from rich.prompt import Prompt

class CLI:
    def __init__(self, verbose: bool = True, width = 100):
        self.console = Console()
        self.verbose = verbose
        self.width = width
        self.padding = (1,4)

    def logo(
        self,
        tool_name: str = "JDEX",
        suite_name: str = "KG-SAF Dataset Generation Suite",
        lab: str = "ARA Laboratory, University of Bari Aldo Moro",
        authors: str = "Ivan Diliso, Roberto Barile",
    ):
        # --- Top header ---
        header = Text(suite_name + "\n", style="bold white")

        # --- ASCII logo ---
        ascii_logo = figlet_format(tool_name, font="slant")
        logo = Text(ascii_logo, style="bold cyan")

        # --- Metadata ---
        year = "2026"

        meta = Text()
        meta.append("KGSAF-JDEX\n", style="bold magenta")
        meta.append("Provided by ", style="dim")
        meta.append(f"{lab}\n", style="bold")
        meta.append("Authors: ", style="dim")
        meta.append(f"{authors}\n", style="bold white")
        meta.append(f"{year}", style="dim")

        # --- Combine everything ---
        content = Text()
        content.append_text(header)
        content.append("\n")
        content.append_text(logo)
        content.append("\n")
        content.append_text(meta)

        # --- Render ---
        self.console.print(
            Panel(
                Align.left(content),
                border_style="bright_blue",
                padding=self.padding,
                width=self.width
            )
        )

    
    def panel(
        self,
        title: str = "None",
        data: list[tuple[str, int]] | None = None
    ):
        data = data or []

        table = Table(
            show_header=False,
            box=None,
            expand=True,
            pad_edge=False
        )

        table.add_column(justify="left")
        table.add_column(justify="right", style="cyan", no_wrap=True)

        for label, value in data:
            table.add_row(str(label), str(value))

        self.console.print(
            Panel(
                table,
                title=title,
                border_style="magenta",
                padding=self.padding,
                width=self.width
            )
        )

    def input(
        self,
        message: str,
        default: str
    ) -> any:
        
        return Prompt.ask(message, default=default)

        

    def list(
        self,
        title: str = "None",
        data: list[str] | None = None
    ):
        data = data or []

        table = Table(
            show_header=False,
            box=None,
            expand=True,
            pad_edge=False
        )

        table.add_column(justify="left")

        for label in data:
            table.add_row(str(label))

        self.console.print(
            Panel(
                table,
                title=title,
                border_style="magenta",
                padding=self.padding,
                width=self.width
            )
        )

    def info(self, message: str):
        if self.verbose:
            self.console.print(f"[bold blue][INFO][/bold blue] {message}")

    def success(self, message: str):
        self.console.print(f"[bold green][ OK ][/bold green] {message}")

    def warning(self, message: str):
        self.console.print(f"[bold yellow][WARN][/bold yellow] {message}")

    def reason(self, message: str):
        self.console.print(f"[bold cyan][REAS][/bold cyan] {message}")


    def error(self, message: str):
        self.console.print(f"[bold red][ERR ][/bold red] {message}")
    
    def _print_fixed(self, renderable):
        self.console.print(renderable, width=self.width)

    def rule(self, title: str = ""):
        self._print_fixed(
            Rule(title, style="green", align="center")
        )

    def subrule(self, title: str = ""):
        self._print_fixed(
            Rule(title, style="dim yellow", align="center")
        )

    def summary(self, title: str, body: str):
        self.console.print(Panel(body, title=title, border_style="magenta", width=self.width, padding=self.padding))

    def choose(self, message: str, choices: list[str]) -> str:
        answer = questionary.select(message, choices=choices).ask()
        if answer is None:
            raise KeyboardInterrupt("Selection cancelled by user.")
        return answer

    def confirm(self, message: str, default: bool = True) -> bool:
        answer = questionary.confirm(message, default=default).ask()
        return bool(answer)
    
    def progress(self, iterable, description: str, total: int | None = None):
        return track(
            iterable,
            description=description,
            total=total,
            console=self.console,
        )
