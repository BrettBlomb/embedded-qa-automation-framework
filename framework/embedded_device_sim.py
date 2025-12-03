# framework/embedded_device_sim.py

import socket
import threading
import time

class TcpEchoServer:
    """Simple TCP echo server to simulate an embedded device."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9000):
        """Initialize TCP echo server with host and port."""
        self.host = host
        self.port = port
        self._server_socket = None
        self._thread = None
        self._running = False

    def _handle_client(self, client_socket: socket.socket):
        """Handle incoming client connections and echo back data."""
        with client_socket:
            while self._running:
                data = client_socket.recv(1024)
                if not data:
                    break
                # Echo bytes back to client
                client_socket.sendall(data)

    def _run(self):
        """Run the main server loop accepting clients."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(5)
        self._running = True

        while self._running:
            try:
                client_socket, _ = self._server_socket.accept()
            except OSError:
                break
            client_thread = threading.Thread(
                target=self._handle_client, args=(client_socket,), daemon=True
            )
            client_thread.start()

    def start(self):
        """Start the TCP echo server in a background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        time.sleep(0.1)  # small delay to ensure server has started

    def stop(self):
        """Stop the TCP echo server and close the socket."""
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        if self._thread:
            self._thread.join(timeout=1)
