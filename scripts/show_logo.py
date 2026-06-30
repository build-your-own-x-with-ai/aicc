#!/usr/bin/env python3
"""Generate colored ASCII logo for AICC."""

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"
ORANGE = "\033[38;5;208m"

def print_logo():
    """Print the AICC logo with colors."""
    print(f"""
{ORANGE}╔═══════════════════════════════════════════════╗{RESET}
{ORANGE}║{RESET}                                               {ORANGE}║{RESET}
{ORANGE}║{RESET}      {CYAN}█████╗ ██╗ ██████╗ ██████╗{RESET}              {ORANGE}║{RESET}
{ORANGE}║{RESET}     {CYAN}██╔══██╗██║██╔════╝██╔════╝{RESET}              {ORANGE}║{RESET}
{ORANGE}║{RESET}     {CYAN}███████║██║██║     ██║{RESET}                   {ORANGE}║{RESET}
{ORANGE}║{RESET}     {CYAN}██╔══██║██║██║     ██║{RESET}                   {ORANGE}║{RESET}
{ORANGE}║{RESET}     {CYAN}██║  ██║██║╚██████╗╚██████╗{RESET}              {ORANGE}║{RESET}
{ORANGE}║{RESET}     {CYAN}╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═════╝{RESET}              {ORANGE}║{RESET}
{ORANGE}║{RESET}                                               {ORANGE}║{RESET}
{ORANGE}║{RESET}          {WHITE}{BOLD}ASCII C Compiler{RESET}                     {ORANGE}║{RESET}
{ORANGE}║{RESET}                                               {ORANGE}║{RESET}
{ORANGE}║{RESET}    {GRAY}C Source{RESET} → {GREEN}ARM64 Assembly{RESET} → {BLUE}Executable{RESET}     {ORANGE}║{RESET}
{ORANGE}║{RESET}                                               {ORANGE}║{RESET}
{ORANGE}╚═══════════════════════════════════════════════╝{RESET}
    """)

def print_banner():
    """Print a simple banner version."""
    print(f"""
{CYAN}{BOLD}   █████  ██ █████  █████{RESET}
{CYAN}{BOLD}  ██   ██ ██ ██    ██    {RESET}
{CYAN}{BOLD}  ███████ ██ ██    ██    {RESET}
{CYAN}{BOLD}  ██   ██ ██ ██    ██    {RESET}
{CYAN}{BOLD}  ██   ██ ██  █████  █████{RESET}

  {WHITE}{BOLD}ASCII C Compiler{RESET}
  {GRAY}Build. Compile. Run.{RESET}
    """)

def print_compact():
    """Print a compact version."""
    print(f"""
{ORANGE}┌─────────────────────────────────────┐{RESET}
{ORANGE}│{RESET}  {CYAN}{BOLD}AICC{RESET} {GRAY}v0.1.0{RESET}                       {ORANGE}│{RESET}
{ORANGE}│{RESET}  {WHITE}ASCII C Compiler{RESET}                  {ORANGE}│{RESET}
{ORANGE}│{RESET}                                     {ORANGE}│{RESET}
{ORANGE}│{RESET}  {GRAY}.c{RESET} → {GREEN}Lex{RESET} → {GREEN}Parse{RESET} → {GREEN}Semantic{RESET}      {ORANGE}│{RESET}
{ORANGE}│{RESET}      → {BLUE}Codegen{RESET} → {MAGENTA}executable{RESET}        {ORANGE}│{RESET}
{ORANGE}└─────────────────────────────────────┘{RESET}
    """)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        style = sys.argv[1]
        if style == "banner":
            print_banner()
        elif style == "compact":
            print_compact()
        else:
            print_logo()
    else:
        print_logo()
