# SerialSocket
TCP Socket with Serial communicaiton

## Usage
```bash
$ ./serial_socket.py -h
usage: serial_socket.py [-h] [-p PORT] [-b BAUDRATE] [-t TIMEOUT] [-s] [-v] [-d]

TCP Socket with Serial communicaiton

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Serial port
  -b BAUDRATE, --baudrate BAUDRATE
                        Serial baudrate
  -t TIMEOUT, --timeout TIMEOUT
                        Serial timeout
  -s, --server          Server mode
  -v, --verbose         Verbose
  -d, --debug           Debug
```

## Example
```bash
$ ./serial_socket.py -p /dev/ttyUSB0 -b 115200 -t 1 -s -v -d
```

## Dependencies
```bash
$ pip install pyserial
```

## Docker
```bash
$ docker build -t serial_socket .
$ docker run -it --rm --device=/dev/ttyUSB0 serial_socket
```

### Docker Compose
```bash
$ docker-compose up
```

## License
[UNLICENSE](https://unlicense.org)

## Author
[Mick K](https://mickk.dk)