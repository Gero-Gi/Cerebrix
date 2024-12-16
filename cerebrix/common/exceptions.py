class CerebrixError(Exception):
    code = "generic_error"
    message = "An error occurred"
    http_status = 500

    def __init__(self, message=None, code=None, http_status=None):
        self.message = message or self.message
        self.code = code or self.code
        self.http_status = http_status or self.http_status

    def get_full_details(self):
        return {"message": self.detail, "code": self.code}
