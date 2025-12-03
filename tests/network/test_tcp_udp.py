# tests/network/test_tcp_udp.py

import socket
import threading
from framework.network_utils import tcp_handshake, send_udp_message

def _udp_server(host: str, port: int, buffer: list):
    """Run a UDP server that stores received messages in buffer."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    while len(buffer) == 0:
        data, _ = sock.recvfrom(1024)
        buffer.append(data)
    sock.close()

def test_tcp_handshake_succeeds_for_localhost():
    """Verify that TCP handshake can succeed for a listening localhost socket."""
    # Start simple listening socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("127.0.0.1", 9200))
    server_sock.listen(1)

    success, msg = tcp_handshake("127.0.0.1", 9200)
    assert success, f"Expected success but got error: {msg}"

    server_sock.close()

def test_udp_message_received_by_server():
    """Verify a UDP message is received by a simple UDP server."""
    host, port = "127.0.0.1", 9300
    buffer = []
    thread = threading.Thread(target=_udp_server, args=(host, port, buffer), daemon=True)
    thread.start()

    send_udp_message(host, port, b"hello_udp")

    # crudely wait for message
    for _ in range(10_000):
        if buffer:
            break

    assert buffer and buffer[0] == b"hello_udp"
