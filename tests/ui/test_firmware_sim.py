# tests/embedded/test_firmware_sim.py

import socket
from framework.embedded_device_sim import TcpEchoServer

def test_tcp_echo_server_round_trip():
    """Verify that the TCP echo server echoes back sent data correctly."""
    server = TcpEchoServer(port=9100)
    server.start()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(("127.0.0.1", 9100))
        message = b"firmware_ping"
        client_socket.sendall(message)
        data = client_socket.recv(1024)
        assert data == message
    finally:
        client_socket.close()
        server.stop()
