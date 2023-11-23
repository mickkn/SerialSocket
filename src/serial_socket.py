"""
:File:        uart_server.py

:Details:     A simple UART server that listens on a TCP socket and forwards the data to the UART and vice versa.

:Copyright:   Copyright (c) 2023 Mick K. All rights reserved.

:Date:        21-11-2023
:Author:      Mick K.
"""
import os
import socket
import threading
import time
import serial
import logging
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def parser():
    """Parse arguments.

    Returns:
        args: The parsed arguments.
    """
    args = ArgumentParser(description="UART Server", formatter_class=ArgumentDefaultsHelpFormatter)
    args.add_argument(
        "-d",
        "--device",
        type=str,
        default="/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AB0LFXWH-if00-port0",
        help="The UART device to use, e.g. /dev/ttyUSB0",
    )
    args.add_argument(
        "-H",
        "--host",
        type=str,
        default="0.0.0.0",
        help="The host to listen on, e.g. 0.0.0.0",
    )
    args.add_argument(
        "-p",
        "--port",
        type=int,
        default=12345,
        help="The port to listen on, e.g. 12345",
    )
    args.add_argument(
        "-b",
        "--baud_rate",
        type=int,
        default=1200,
        help="The baud rate to use, e.g. 9600",
    )
    args.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=3600.0 * 2,
        help="The timeout in seconds for the socket and the UART, e.g. 20.0",
    )
    print("\n" + str(args.parse_args()) + "\n")
    return args.parse_args()


class SerialSocket:
    """A simple UART server that listens on a TCP socket and
    forwards the data to the UART and vice versa.
    """

    def __init__(
        self,
        _device: str,
        _host: str,
        _baud_rate: int,
        _port: int,
        _timeout: float = 5.0,
    ):
        """Initializes the UART server.

        Args:
            _device: The UART device to use, e.g. /dev/ttyUSB0
            _host: The host to listen on, e.g. 0.0.0.0
            _baud_rate: The baud rate to use, e.g. 1200
            _port: The port to listen on, e.g. 12345
            _timeout: The timeout in seconds for the socket and the UART, e.g. 5.0
        """
        self._host = _host
        self._port = _port
        self._timeout = _timeout
        self._serial = serial.Serial(_device, _baud_rate)
        self._serial.timeout = _timeout
        self._server_socket = None
        self._client_socket = None
        logging.basicConfig(level=logging.DEBUG,
                            format="[%(asctime)s] [%(levelname)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S",
                            )
        self.logger = logging.getLogger(__name__)

    def _socket_to_serial(self):
        """Read from socket and send to UART"""
        try:
            while True:
                data = self._client_socket.recv(1024)
                self.logger.debug(f"Received data: {data}")
                if len(data) == 0:
                    break  # Client closed connection or timed out.
                self._serial.write(data)
        except KeyboardInterrupt:
            pass
        except TimeoutError:
            self.logger.info("Socket timeout. Restarting server...")
        except Exception as e:
            self.logger.error(f"Error in communication with client: {e}")

    def _serial_to_socket(self):
        """Read from UART and send to socket"""
        try:
            while True:
                data = self._serial.read(1)
                if len(data) == 0:
                    break  # Client closed connection or timed out.
                self._client_socket.send(data)
        except KeyboardInterrupt:
            pass
        except TimeoutError:
            self.logger.info("Serial interface timeout. Restarting server...")
        except Exception as e:
            self.logger.error(f"Error in communication with client: {e}")

    def start(self):
        """Start the endless loop of reading from Client and writing back to Client"""

        while True:
            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                self._server_socket.settimeout(self._timeout)
                self._server_socket.bind((self._host, self._port))
                self._server_socket.listen(1)  # Listen for one connection at a time
                self.logger.info(f"UART Socket Server listening on {self._host}:{self._port}")
                self._client_socket, client_address = self._server_socket.accept()
                self._client_socket.settimeout(self._timeout)
                self.logger.info(f"Connection from {client_address}")
                from_thread = threading.Thread(target=self._socket_to_serial, daemon=True)
                from_thread.start()
                to_thread = threading.Thread(target=self._serial_to_socket, daemon=True)
                to_thread.start()

                from_thread.join()
                to_thread.join()

                self._client_socket.close()

                self.logger.debug("Threads joined")

            except TimeoutError:
                self.logger.info("Timeout. Restarting server...")
                continue
            except KeyboardInterrupt:
                self.logger.info("\nServer terminated by user.")
                break
            except Exception as e:
                self.logger.error(f"Error in server: {e}")
                break
            finally:
                self.logger.info("Closing sockets...")
                if self._client_socket:
                    self._client_socket.close()
                if self._server_socket:
                    self._server_socket.close()
                time.sleep(2)


if __name__ == "__main__":
    args = parser()

    # Get settings from environment variables.
    device = os.getenv("DEVICE", args.device)
    host = os.getenv("HOST", args.host)
    port = int(os.getenv("PORT", args.port))
    baud_rate = int(os.getenv("BAUD_RATE", args.baud_rate))
    timeout = float(os.getenv("TIMEOUT", args.timeout))

    uart_server = SerialSocket(device, host, baud_rate, port, timeout)
    uart_server.start()
