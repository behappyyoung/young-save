import socket

if socket.gethostbyname(socket.gethostname()) == "IP address":
    DEBUG = True
else:
    DEBUG = False
    ALLOWED_HOSTS = ["*",]



