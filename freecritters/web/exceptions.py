class Redirect302(Exception):
    def __init__(self, new_url):
        self.new_url = new_url
        Exception.__init__(self, new_url)

class Error304(Exception):
    pass

class Error401RSS(Exception):
    pass

class Error403(Exception):
    pass

class Error404(Exception):
    pass