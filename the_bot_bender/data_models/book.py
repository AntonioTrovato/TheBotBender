class Book():
    def __init__(self, title: str = None, author: str = "", description: str = "", image: str = "",
                 google_play: str = "", self_link: str = ""):
        if author == None:
            author = ""
        elif description == None:
            description = ""
        elif image == None:
            image = ""
        elif google_play == None:
            google_play = ""
        self.title = title
        self.author = author
        self.description = description
        self.image = image
        self.google_play = google_play
        self.self_link = self_link
