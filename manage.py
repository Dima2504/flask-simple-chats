from app import make_app
from app import socket_io


if __name__ == '__main__':
    socket_io.run(make_app())
