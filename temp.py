import requests
import os
def search_movie(title):
    api_read_key = os.getenv('API_READ_ACCESS')

    url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_read_key}"
    }

    response = requests.get(url, headers=headers)

    # print(response.text)
    return response.json().get('results', [])

api_response = search_movie('The Godfather')

print(api_response[:5])