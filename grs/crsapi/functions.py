
class CustomError(Exception):
    def __init__(self, arg):
        self.error_string = arg
        self.args = {arg}


def get_remote_id(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        remote_ip = x_forwarded_for.split(',')[0]
    else:
        remote_ip = request.META.get('REMOTE_ADDR')
    return remote_ip

