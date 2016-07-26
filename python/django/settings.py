import socket

if socket.gethostname() == "local computer name":
    DEBUG = True
    ALLOWED_HOSTS = ["localhost", "127.0.0.1",]
else:
    DEBUG = False
    ALLOWED_HOSTS = [".your_domain_name.com",]



