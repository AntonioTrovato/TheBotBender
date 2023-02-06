class UserProfile:
    """
      This class models a generic bot user
    """

    def __init__(self, id: str, name: str = None, surname: str = None,
                 city: str = None, favorite_books: list = []):
        self.id = id
        self.name = name
        self.surname = surname
        self.city = city
        self.favorite_books = favorite_books
