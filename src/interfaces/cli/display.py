"""CLI display components and utilities."""

import os
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns

from ...config.settings import settings
from ...i18n.manager import i18n

console = Console()

class DisplayManager:
    """Manage CLI display components."""

    def __init__(self):
        """Initialize display manager."""
        self.console = Console()

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def show_banner(self) -> None:
        """Display application banner."""
        self.clear_screen()
        self.console.print(
            Panel(
                r"""[bold red]●[bold yellow] ●[bold green] ●
[bold blue]                  _    _ _   _           
[bold blue]                 | |  | | | | |          
[bold blue]                 | |__|_  _|| |__        
[bold blue]                 |____| |_| |____|       
[bold purple]              ___        _  _        
[bold purple]             / __| _  _ (_)| |_  ___ 
[bold purple]             \__ \| || || ||  _|/ -_)
[bold purple]             |___/ \_,_||_| \__|\___|
                               

                  [bold white on blue]Coded by LavX""",
                width=55,
                style="bold bright_white",
            )
        )
    def show_status(self, credits: str) -> None:
        """Display status panel.
        
        Args:
            credits: Current credit balance
        """
        self.console.print(
            Panel(
                f"[bold white]{i18n.get_text('status.coins')} :[bold red] {credits}",
                width=55,
                style="bold bright_white",
                title=f"[bold bright_white]>> [{i18n.get_text('status.status')}] <<"
            )
        )

    def show_menu(self) -> None:
        """Display main menu."""
        self.console.print(
            Panel(
                f"""[bold yellow]0[bold white] Run All Features

[bold cyan]Profile Management[bold white]
[bold green]1[bold white] {i18n.get_text('menu.exchange_profile')}
[bold green]2[bold white] {i18n.get_text('menu.exchange_page')}

[bold cyan]Twitter Features[bold white]
[bold green]3[bold white] Twitter Follow Mission
[bold green]4[bold white] Twitter Like Mission
[bold green]5[bold white] Twitter Retweet Mission

[bold cyan]Facebook Features[bold white]
[bold green]6[bold white] Facebook Follow Mission
[bold green]7[bold white] Facebook Profile Follow Mission
[bold green]8[bold white] Facebook Like Mission
[bold green]9[bold white] Facebook Share Mission
[bold green]10[bold white] Facebook Comment Mission

[bold cyan]Instagram Features[bold white]
[bold green]11[bold white] Instagram Follow Mission
[bold green]12[bold white] Instagram Like Mission
[bold green]13[bold white] Instagram Comment Mission

[bold cyan]TikTok Features[bold white]
[bold green]14[bold white] TikTok Follow Mission
[bold green]15[bold white] TikTok Like Mission

[bold cyan]Pinterest Features[bold white]
[bold green]16[bold white] Pinterest Follow Mission
[bold green]17[bold white] Pinterest Repin Mission

[bold cyan]SoundCloud Features[bold white]
[bold green]18[bold white] SoundCloud Like Mission
[bold green]19[bold white] SoundCloud Follow Mission

[bold cyan]Other Platforms[bold white]
[bold green]20[bold white] MySpace Connect Mission
[bold green]21[bold white] ReverbNation Fan Mission
[bold green]22[bold white] OK.ru Join Mission

[bold cyan]Management[bold white]
[bold green]23[bold white] {i18n.get_text('menu.delete_links')}
[bold green]24[bold white] {i18n.get_text('menu.switch_language')}
[bold green]25[bold white] {i18n.get_text('menu.exit')}""",
                width=55,
                style="bold bright_white",
                subtitle="╭─────",
                subtitle_align="left",
                title="[bold bright_white]>> [Menu] <<"
            )
        )

    def show_language_menu(self) -> None:
        """Display language selection menu."""
        self.console.print(
            Panel(
                f"""[bold white]1. {i18n.get_text('menu.language.english')}
2. {i18n.get_text('menu.language.indonesian')}""",
                width=55,
                style="bold bright_white",
                title=f"[bold bright_white]>> [{i18n.get_text('menu.language.select')}] <<",
                subtitle="╭─────",
                subtitle_align="left"
            )
        )

    def show_success(self, message: str, width: int = 55) -> None:
        """Display success message.
        
        Args:
            message: Success message
            width: Panel width
        """
        self.console.print(
            Panel(
                f"[bold green]{message}",
                width=width,
                style="bold bright_white",
                title=f"[bold bright_white]>> [{i18n.get_text('status.success')}] <<"
            )
        )

    def show_error(self, message: str, width: int = 55) -> None:
        """Display error message.
        
        Args:
            message: Error message
            width: Panel width
        """
        self.console.print(
            Panel(
                f"[bold red]{message}",
                width=width,
                style="bold bright_white",
                title=f"[bold bright_white]>> [{i18n.get_text('status.error')}] <<"
            )
        )

    def show_notice(self, message: str, width: int = 55) -> None:
        """Display notice message.
        
        Args:
            message: Notice message
            width: Panel width
        """
        self.console.print(
            Panel(
                f"[bold white]{message}",
                width=width,
                style="bold bright_white",
                title=f"[bold bright_white]>> [{i18n.get_text('status.wait')}] <<"
            )
        )

    def show_progress(self,
        message: str,
        success_count: int = 0,
        fail_count: int = 0
    ) -> None:
        """Display progress message.
        
        Args:
            message: Progress message
            success_count: Number of successful operations
            fail_count: Number of failed operations
        """
        self.console.print(
            f"[bold white]   ──>[bold white] {i18n.get_text('status.mission_progress')} [{i18n.get_text('status.success_count')}:-[bold green]{success_count}[bold white] {i18n.get_text('status.failed_count')}:-[bold red]{fail_count}[bold white]]     ",
            end="\r"
        )

    def prompt(self, message: str) -> str:
        """Show input prompt.
        
        Args:
            message: Prompt message
            
        Returns:
            str: User input
        """
        return self.console.input(f"[bold bright_white]   ╰─> {message}")

    def show_task_result(self,
        task_type: str,
        target_url: str,
        old_credits: str,
        new_credits: str
    ) -> None:
        """Display task result panel.
        
        Args:
            task_type: Type of task completed
            target_url: Target URL
            old_credits: Previous credit balance
            new_credits: New credit balance
        """
        self.console.print(
            Panel(
                f"""[bold white]{i18n.get_text('status.status')} :[bold green] {i18n.get_text('status.success')}...
[bold white]{task_type} :[bold red] {target_url}
[bold white]{i18n.get_text('status.coins')} :[bold green] {old_credits}[bold white] >[bold green] {new_credits}""",
                width=55,
                style="bold bright_white",
                title=f"[bold bright_white]>> [{i18n.get_text('status.success')}] <<"
            )
        )