class Library:
    def __init__(self, name: str, address: str, email: str = None):
        if email == None:
            email = ""
        if address == None:
            address = ""
        self.name = name
        self.address = address
        self.email = email
