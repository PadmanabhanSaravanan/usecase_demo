class User:
    def __init__(self, id: int, username: str, hashed_password: str, role: str):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.role = role
