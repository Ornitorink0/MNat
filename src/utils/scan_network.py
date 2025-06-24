import pathlib
import csv
import socket
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from scapy.all import ARP, Ether, srp
import click


def get_hostname(ip: str, timeout: int = 1) -> str:
    """
    Resolve an IP address to its hostname.

    Args:
        ip (str): IP address to resolve.
        timeout (int, optional): Timeout in seconds for the DNS query. Defaults to 1.

    Returns:
        str: Hostname for the given IP address, or "N/D" if the query fails.
    """
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.timeout, Exception):
        return "N/D"


def resolve_hostnames(devices):
    """
    Resolve hostnames for a list of devices.

    Args:
        devices (list[dict]): List of devices with IP and MAC addresses.

    Returns:
        list[dict]: List of devices with IP, MAC, and Hostname addresses.
    """
    print("[+] Resolving hostnames...")
    total = len(devices)

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(get_hostname, device["IP"]): device for device in devices
        }

        for i, future in enumerate(as_completed(futures), 1):
            device = futures[future]
            device["Hostname"] = future.result()
            print(
                f"    [{i}/{total}] {device['IP']} → {device['MAC']} → {device['Hostname']}"
            )
    return devices


def scan_network(ip_range: str, subnet: str, output_dir: pathlib.Path = None) -> bool:
    print(f"[+] Scanning network: {ip_range}{subnet}")
    start_time = time.time()

    arp_request = ARP(pdst=f"{ip_range}{subnet}")
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether_frame / arp_request

    answered, _ = srp(packet, timeout=2, verbose=0)

    devices = [
        {"IP": response.psrc, "MAC": response.hwsrc, "Hostname": "N/A"}
        for _, response in answered
    ]

    if not devices:
        print("[!] No devices found.")
        return False

    print(f"[+] Found {len(devices)} devices...")
    devices = resolve_hostnames(devices)

    elapsed_time = time.time() - start_time
    print(f"[✓] Scan completed in {elapsed_time:.2f} seconds.")

    if output_dir is not None:
        save_results(devices, output_dir)
    else:
        while True:
            response = (
                input(
                    "Do you want to save the results? (Press Enter to continue without saving): "
                )
                .strip()
                .lower()
            )
            if not response:
                break
            if response in ["y", "yes"]:
                save_results(devices, output_dir)
                break
            elif response in ["n", "no"]:
                break
            else:
                click.secho("Invalid response. Please try again.", fg="yellow")

    return True


def save_results(devices, output_path=None):
    output_path = Path(output_path)
    if output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = output_path / f"mnet.scan.{timestamp}.csv"
    else:
        output_file = output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open(mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["IP", "MAC", "Hostname"])
        writer.writeheader()
        writer.writerows(devices)

    print(f"[✓] Saved results to: {output_file}")
