# schema dell'oggetto json ricevuto dalla function app
class ProactiveRequest:
    def __init__(self, body: dict) -> None:
        if body["image"] == None:
            body["image"] = ""
        self.name = body["name"].replace("<b>","").replace("</b>","").replace("<p>","").replace("</p>","")\
            .replace("<br>","").replace("</br>","").replace("&#39;","'")
        self.url = body["url"]
        self.description = body["description"].replace("<b>","").replace("</b>","").replace("<p>","")\
            .replace("</p>","").replace("<br>","").replace("</br>","").replace("&#39;","'")
        self.image = body["image"]
        self.date = body["date"][0:10]