from .. import socket_io


@socket_io.on('connect', namespace='/chats/going')
def c():
    print('connected')

