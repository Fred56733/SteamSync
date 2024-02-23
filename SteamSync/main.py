from flask import Flask, render_template, request, url_for, jsonify
import http.client
import json
import re
import requests
import urllib.parse

app = Flask(__name__)

RAPIDAPI_KEY = "887b3f8b15mshbd3fe8a5db8cdefp19c527jsnfc5aacbdb5ad"
GAMESPOTAPI_KEY = "15db3545ca5bec59186fca6096262dfacf0c7659"
RAPIDAPI_HOST = "steam2.p.rapidapi.com"
GAME_SPOT_API_BASE_URL = "https://www.gamespot.com/api"


def sanitize_input(input_str):
    return re.sub(r'[^a-zA-Z0-9]', '', input_str)


@app.route("/", methods=['GET'])
def login():
    return render_template("index.html")


@app.route("/get-steam-user-summary/<steamId>", methods=['GET'])
def get_steam_user_summary(steamId):
    steamApiKey = "E4ABF7871264272AD62B7798CCF512DC"
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steamApiKey}&steamids={steamId}"
    response = requests.get(url)
    return response.json()


def get_reviews_for_app(appId, limit=40):
    conn = http.client.HTTPSConnection("steam2.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }

    endpoint = f"/appReviews/{appId}/limit/{limit}/*"
    conn.request("GET", endpoint, headers=headers)

    res = conn.getresponse()
    reviews_data = json.loads(res.read().decode("utf-8"))

    return reviews_data


@app.route("/home_with_news", methods=['GET'])
def gamespot_articles():
    # Define the endpoint and parameters for the Gamespot articles API
    gamespot_api_key = "15db3545ca5bec59186fca6096262dfacf0c7659"
    gamespot_endpoint = "https://www.gamespot.com/api/articles/"
    params = {
        'api_key': gamespot_api_key,
        'format': 'json',
        'limit': 100  # or any other parameters you need
    }

    headers = {
        'User-Agent': 'SteamSync'  # Use your unique User-Agent here
    }

    try:
        # Make the request to the Gamespot API
        response = requests.get(gamespot_endpoint, params=params, headers=headers)
        response.raise_for_status()  # Raise an HTTPError if an error occurred

        # Parse the JSON response
        articles_data = response.json()

        # Check if 'results' key is present in the response
        articles = articles_data.get('results', [])

    except requests.exceptions.RequestException as e:
        # Handle exceptions (print, log, or return an error response)
        print(f"Error fetching Gamespot articles: {e}")
        if response and response.status_code == 403:
            print("Forbidden: Check your API key, rate limits, and endpoint access.")
        articles = []

    # Now, make an additional call to the image gallery API
    # for article in articles:
    #     image_gallery_endpoint = f"https://www.gamespot.com/api/image_galleries/?api_key={gamespot_api_key}&filter=id:{article['id']}&format=json"
    #     image_response = requests.get(image_gallery_endpoint, headers=headers)
    #     image_gallery_data = image_response.json()
    #
    #     if image_gallery_data.get('results'):
    #         # gallery = image_gallery_data['results'][0]
    #         # article['gallery_image'] = gallery['image']['original']
    #         original_image_url = image_gallery_data['results'][0]['image']['original']
    #         article['gallery_image'] = original_image_url

    # Render the template with Gamespot articles
    return render_template("home_with_news.html", articles=articles)


@app.route("/home", methods=['GET'])  # Using the root path for homepage
def home():
    conn = http.client.HTTPSConnection("steam-store-data.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': 'f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e',
        'X-RapidAPI-Host': 'steam-store-data.p.rapidapi.com'
    }

    conn.request("GET", "/api/featuredcategories/", headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))

    categories = {k: v for k, v in data.items() if isinstance(v, dict) and 'items' in v}

    # Adding detail URLs to each item using the game's ID
    for category in categories.values():
        for item in category['items']:
            if 'id' in item:
                item['detail_url'] = url_for('game_detail', game_id=item['id'])
            else:
                print(f"Missing ID for item: {item.get('name', 'Unknown Item')}")

    return render_template("home.html", categories=categories)


@app.route("/Discounted_games", methods=['GET'])
def Discounted_games():
    conn = http.client.HTTPSConnection("steam-store-data.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': 'f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e',
        'X-RapidAPI-Host': 'steam-store-data.p.rapidapi.com'
    }

    conn.request("GET", "/api/featuredcategories/", headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))

    categories = {k: v for k, v in data.items() if isinstance(v, dict) and 'items' in v}

    # Adding detail URLs to each item using the game's ID
    for category in categories.values():
        for item in category['items']:
            if 'id' in item:
                item['detail_url'] = url_for('game_detail', game_id=item['id'])
            else:
                print(f"Missing ID for item: {item.get('name', 'Unknown Item')}")

    return render_template("Discounted_games.html", categories=categories)


@app.route("/game/<int:appid>/news", methods=['GET'])
def game_news(appid):
    conn = http.client.HTTPSConnection("steam2.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }

    endpoint = f"/newsForApp/{appid}/limit/10/300"  # Use the app_id dynamically
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))

    # Debugging: Print the data to see if it contains news items
    print(data)

    if 'appnews' in data and 'newsitems' in data['appnews']:
        newsitems = data['appnews']['newsitems']
        # Debugging: Print the news_items
        print(newsitems)
    else:
        newsitems = []

    # Debugging: Print a message if no news items were found
    if not newsitems:
        print("No news items found.")

    # Change this to the template you're actually using for game details
    return render_template("gamedetails.html", news=newsitems, appid=appid)


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return render_template("search.html", error="Please enter a search query.", games=[])

    print(f"Query before encoding: {query}")
    encoded_query = urllib.parse.quote_plus(query)
    print(f"Query after encoding: {encoded_query}")

    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }

    endpoint = f"/search/{encoded_query}/page/1"
    print(f"Endpoint: {endpoint}")
    print(f"Headers: {headers}")

    try:
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        print(f"Status Code: {res.status}")

        response_data = json.loads(res.read().decode("utf-8"))
        print(f"Response: {response_data}")

        games = response_data  # This assumes the response is a list of games. Adjust accordingly if it's not.

    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {e}")
        return render_template("search.html", error="Failed to fetch game results. Please try again.", games=[])

    if not games:
        return render_template("search.html", error="No games found for the given query.", games=[])

    return render_template("search.html", games=games)


@app.route("/game/<int:game_id>", methods=['GET'])
def game_detail(game_id):
    conn = http.client.HTTPSConnection("steam2.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }

    # Fetching game details
    conn.request("GET", f"/appDetail/{game_id}", headers=headers)
    res = conn.getresponse()
    game = json.loads(res.read().decode("utf-8"))

    # Fetching game reviews
    conn.request("GET", f"/appReviews/{game_id}/limit/40/*", headers=headers)
    res_reviews = conn.getresponse()
    reviews_data = json.loads(res_reviews.read().decode("utf-8"))
    reviews = reviews_data['reviews'][:10]  # extracting the first 10 reviews

    # Fetching game news
    endpoint = f"/newsForApp/{game_id}/limit/10/300"  # Use the game_id dynamically
    conn.request("GET", endpoint, headers=headers)
    res_news = conn.getresponse()
    news_data = json.loads(res_news.read().decode("utf-8"))
    newsitems = news_data.get('appnews', {}).get('newsitems', [])[:5]

    # Rendering the template with game details, reviews, and news
    return render_template("game_detail.html", game=game, reviews=reviews, news=newsitems)


if __name__ == "__main__":
    app.run(debug=True)



