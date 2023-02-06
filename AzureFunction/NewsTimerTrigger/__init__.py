import azure.functions as func

import requests

import datetime

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    send_news()

def send_news():
    subscription_key = ""
    search_term = "letteratura"
    search_url = "https://api.bing.microsoft.com/v7.0/news/search"

    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params  = {"q": search_term, "textDecorations": True, "textFormat": "HTML", "mkt": "it-IT"}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    news = []

    i = 0

    for the_single_news in search_results["value"]:
        if(i >= 3):
            break
        name = ""
        url = ""
        description = ""
        image = ""
        date = ""
        if "name" in the_single_news.keys():
            name = the_single_news["name"]
        if "url" in the_single_news.keys():
            url = the_single_news["url"]
        if "description" in the_single_news.keys():
            description = the_single_news["description"]
        if "image" in the_single_news.keys() and "thumbnail" in the_single_news["image"].keys() and "currentUrl" in the_single_news["image"]["thumbnail"]:
            image = the_single_news["image"]["thumbnail"]["currentUrl"]
        if "date" in the_single_news.keys():
            date = the_single_news["datePublished"]
        a_single_news = {"name":name,"url":url,"description":description,"image":image,"date":date}
        news.append(a_single_news)
        i = i + 1
    
    body = {"news":news}

    requests.get("https://TheBotBenderAppService.azurewebsites.net/api/notify",headers={"Content-Type":"application/json"},json=body)
