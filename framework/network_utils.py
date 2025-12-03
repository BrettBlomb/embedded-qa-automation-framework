# framework/network_utils.py

import socket
from typing import Tuple

def send_udp_message(host: str, port: int, message: bytes) -> None:
    """Send a UDP message to the specified host and port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message, (host, port))
    finally:
        sock.close()

def tcp_handshake(host: str, port: int, timeout: float = 3.0) -> Tuple[bool, str]:
    """Attempt a TCP connection to test handshake success."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True, "Connection succeeded"
    except Exception as ex:
        return False, str(ex)
    finally:
        sock.close()
