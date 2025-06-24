import os
from pathlib import Path
import click
import ipaddress
import platform
import ctypes
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
import utils.scan_network as scan


def check_permissions():
    """Check if the script is run with sufficient permissions."""

    system = platform.system()
    if system == "Linux" or system == "Darwin":
        if os.geteuid() != 0:
            click.secho(
                "   ⚠️  Warning: It is recommended to run this application as root (sudo) for full functionality.\n",
                fg="yellow",
            )
    elif system == "Windows":
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            is_admin = False
        if not is_admin:
            click.secho(
                "   ⚠️  Warning: It is recommended to run this application as Administrator for full functionality.\n",
                fg="yellow",
            )
    else:
        click.secho(
            "   ⚠️  Warning: Unknown operating system. Permission checks may not be accurate.\n",
            fg="yellow",
        )


def splash_screen():
    """Display a splash screen with application information."""
    click.clear()
    click.secho(
        "╔════════════════════════════════════════════════════════╗",
        fg="green",
        bold=True,
    )
    click.secho(
        "║   __  __ _   _      _                                  ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "║  |  \\/  | \\ | | ___| |_   MNat Network Utility         ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "║  | |\\/| |  \\| |/ _ \\ __|                               ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "║  | |  | | |\\  |  __/ |_   Created by: Ornitorink0      ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "║  |_|  |_|_| \\_|\\___|\\__|  Version: 0.1.0               ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "║                                                        ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "║  Github: https://github.com/Ornitorink0                ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "║  License: GNU General Public License v3.0              ║",
        fg="green",
        bold=True,
    )
    click.secho(
        "╚════════════════════════════════════════════════════════╝",
        fg="green",
        bold=True,
    )
    click.echo()
    click.secho(
        " ` * ★ Welcome to the MNat Network Utility! ★ * `",
        fg="bright_yellow",
        bold=True,
    )
    click.secho(
        "   Follow the prompts to set up your network IP and subnet mask.",
        fg="bright_yellow",
    )
    click.echo()


history = FileHistory(".mnat_prompt_history")


def prompt_for_netip():
    while True:
        netip = prompt(
            "Enter the network IP address (e.g., 244.178.44.111): ", history=history
        ).strip()
        if validate_netip(netip):
            if confirm_netip(netip):
                return netip


def validate_netip(netip):
    try:
        ipaddress.IPv4Address(netip)
    except ValueError:
        click.secho(
            "Invalid network IP address format. Use 'x.x.x.x' format.\n", fg="red"
        )
        return False

    if not netip:
        click.secho("❌ Network IP address cannot be empty.", fg="red")
        return False

    return True


def confirm_netip(netip):
    if netip == "0.0.0.0":
        while True:
            response = (
                prompt(
                    "⚠️ Are you sure you want to use 0.0.0.0? (y/n): ",
                    history=history,
                )
                .strip()
                .lower()
            )
            if response == "y":
                return True
            elif response == "n":
                return False
            else:
                click.secho("Please enter a valid response: 'y' or 'n'.", fg="red")
    return True


def prompt_for_subnet():
    while True:
        subnet = prompt("Enter the subnet mask (e.g., /24): ", history=history).strip()
        if validate_subnet(subnet):
            if confirm_subnet(subnet):
                return subnet


def validate_subnet(subnet):
    if not subnet:
        click.secho("❌ Subnet mask cannot be empty.", fg="red")
        return False

    if (
        not subnet.startswith("/")
        or not subnet[1:].isdigit()
        or not (0 <= int(subnet[1:]) <= 32)
    ):
        click.secho(
            "❌ Invalid subnet format. Use format like /24 (between /0 and /32).\n",
            fg="red",
        )
        return False
    return True


def confirm_subnet(subnet):
    if int(subnet[1:]) <= 16:
        while True:
            response = (
                prompt(
                    f"⚠️ Are you sure you want to use subnet {subnet}? (y/n): ",
                    history=history,
                )
                .strip()
                .lower()
            )
            if response == "y":
                click.secho(
                    f"\n  Caution: Using a large subnet like {subnet} may expose your network and the tasks may take longer.",
                    fg="yellow",
                )
                click.secho(
                    "   Ensure you understand the implications of using a large subnet.\n",
                    fg="yellow",
                )
                return True
            elif response == "n":
                return False
            else:
                click.secho("Please enter a valid response: 'y' or 'n'.", fg="red")
    return True


@click.command()
@click.option("--netip", help="Network IP address to bind to.")
@click.option("--subnet", help="Subnet mask to use (e.g., /24).")
@click.option(
    "--out",
    type=click.Path(file_okay=True, dir_okay=True, writable=True, resolve_path=True),
    help="Path to save the output file (optional). Can be a file or a directory.",
)
@click.pass_context
def netip_command(ctx, netip, subnet, out):
    """Run the application with the specified network IP address."""

    splash_screen()
    check_permissions()

    netip = (
        netip or prompt_for_netip()
        if not netip
        else (
            netip
            if validate_netip(netip) and confirm_netip(netip)
            else prompt_for_netip()
        )
    )
    subnet = (
        subnet or prompt_for_subnet()
        if not subnet
        else (
            subnet
            if validate_subnet(subnet) and confirm_subnet(subnet)
            else prompt_for_subnet()
        )
    )

    while True:
        click.secho(
            "Please confirm the network settings:",
            fg="cyan",
            bold=True,
        )
        click.secho(f"Network IP: {netip}", fg="green")
        click.secho(f"Subnet Mask: {subnet}", fg="green")
        response = prompt("Is this correct? (y/n): ", history=history).strip().lower()
        if response == "y":
            break
        elif response == "n":
            click.secho("Let's re-enter the network settings.", fg="cyan")
            netip = prompt_for_netip()
            subnet = prompt_for_subnet()
        else:
            click.secho("Please enter a valid response: 'y' or 'n'.", fg="red")

    # If all checks pass, print the network IP and subnet
    print(f"Running application on network IP: {netip}{subnet}")

    output_path = None
    if out:
        output_path = Path(out)
        if not output_path.exists():
            if output_path.suffix:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_path.mkdir(parents=True, exist_ok=True)
        elif output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)
        elif output_path.is_file():
            output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path:
        click.secho(f"Output will be saved to: {output_path}", fg="green")
    else:
        click.secho("Output will NOT be saved (no --out provided)", fg="yellow")

    while True:
        click.secho("\nWhat do you want to do?", fg="cyan", bold=True)
        click.secho("1. Scan for MAC addresses", fg="green")
        click.secho("0. Exit the application", fg="red")
        response = prompt("Enter the number of your choice: ", history=history).strip()
        try:
            choice = int(response)
        except ValueError:
            click.secho("Please enter a valid number.", fg="red")
            continue

        # --------------------------- MAC ADDRESS SCANNING --------------------------- #
        if choice == 1:
            click.secho("\nStarting MAC address scanning...", fg="cyan")
            try:
                scan.scan_network(netip, subnet, output_path)
                click.secho("MAC address scanning completed successfully.", fg="green")
            except Exception as e:
                click.secho(f"An error occurred during scanning: {e}", fg="red")

        # --------------------------- EXIT THE APPLICATION --------------------------- #
        elif choice == 0:
            click.secho("\nExiting the application...", fg="cyan")
            break
        else:
            click.secho("Please enter a valid choice.", fg="red")


if __name__ == "__main__":
    netip_command()
