import os
import requests
import pandas as pd
import time
from tqdm import tqdm
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ====================================
# Load Environment Variables
# ====================================
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env file")

BASE_URL = "https://api.themoviedb.org/3"
TOTAL_PAGES = 50  # Adjust as needed

# ====================================
# Create Session with Retry Logic
# ====================================

def create_session():
    session = requests.Session()

    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session

session = create_session()

# ====================================
# Helper Functions
# ====================================

def get_movies(page):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": page
    }
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["results"]


def get_movie_full_details(movie_id):
    """
    Single API call using append_to_response
    This replaces both get_movie_details and get_movie_credits
    """
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "append_to_response": "credits"
    }
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


# ====================================
# Main Logic
# ====================================

def run_ingestion():
    all_movies = []

    for page in range(1, TOTAL_PAGES + 1):
        print(f"\nFetching page {page}")

        try:
            movies = get_movies(page)
        except Exception as e:
            print(f"Failed to fetch page {page}: {e}")
            continue

        for movie in tqdm(movies):
            movie_id = movie["id"]

            try:
                details = get_movie_full_details(movie_id)

                genres = ", ".join([g["name"] for g in details.get("genres", [])])

                cast = details.get("credits", {}).get("cast", [])[:5]
                actors = ", ".join([actor["name"] for actor in cast])

                movie_data = {
                    "movie_id": movie_id,
                    "title": details.get("title"),
                    "release_date": details.get("release_date"),
                    "runtime": details.get("runtime"),
                    "genres": genres,
                    "rating": details.get("vote_average"),
                    "vote_count": details.get("vote_count"),
                    "actors": actors,
                    "overview": details.get("overview")
                }

                all_movies.append(movie_data)

                # delay
                time.sleep(0.5)

            except Exception as e:
                print(f"Error processing movie {movie_id}: {e}")
                continue

    # ====================================
    # Save to data folder
    # ====================================

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "movies.csv")

    df = pd.DataFrame(all_movies)
    df.to_csv(output_path, index=False)

    print(f"\nSaved {len(df)} movies to {output_path}")


if __name__ == "__main__":
    run_ingestion()
