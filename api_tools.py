from crewai.tools import tool
from typing import Dict, Any, List, Optional
import requests
import json

@tool
def search_movies(api_key: str, read_access_token: str, search_criteria: Dict[str, Any], count: int = 10) -> List[Dict]:
    """
    Search for movies based on search criteria using The Movie Database (TMDB) API
    
    Args:
        api_key: TMDB API key
        read_access_token: TMDB read access token
        search_criteria: Dictionary containing search parameters (genre, actor, director, year, min_rating)
        count: Number of results to return
        
    Returns:
        List of movie dictionaries with details
    """
    tmdb_tools = TMDBMovieTools(api_key, read_access_token)
    return tmdb_tools.search_movies(search_criteria, count)

@tool
def search_music(search_criteria: Dict[str, Any], count: int = 10) -> List[Dict]:
    """
    Search for music based on search criteria using iTunes Search API
    
    Args:
        search_criteria: Dictionary containing search parameters (artist, genre, term)
        count: Number of results to return
        
    Returns:
        List of music dictionaries with details
    """
    itunes_tools = ITunesMusicTools()
    return itunes_tools.search_music(search_criteria, count)

@tool
def fetch_news(api_key: str, search_query: str, count: int = 5) -> List[Dict]:
    """
    Fetch news articles based on search query using SERP API
    
    Args:
        api_key: SERP API key
        search_query: News topic or search term
        count: Number of news articles to return
        
    Returns:
        List of news article dictionaries
    """
    news_tools = NewsTools(api_key)
    return news_tools.fetch_news(search_query, count)

@tool
def web_search(api_key: str, query: str, count: int = 10) -> Dict:
    """
    Perform a general web search using SERP API
    
    Args:
        api_key: SERP API key
        query: Search query
        count: Number of results to return
        
    Returns:
        Dictionary with search results and knowledge graph if available
    """
    search_tools = GeneralSearchTools(api_key)
    return search_tools.web_search(query, count)


# Helper classes (not directly exposed as tools)
class TMDBMovieTools:
    """Tools for searching movies using The Movie Database (TMDB) API"""
    
    def __init__(self, api_key, read_access_token):
        self.api_key = api_key
        self.read_access_token = read_access_token
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {self.read_access_token}",
            "Content-Type": "application/json;charset=utf-8"
        }
    
    def search_movies(self, search_criteria: Dict[str, Any], count: int = 10) -> List[Dict]:
        """
        Search for movies based on search criteria
        
        Args:
            search_criteria: Dictionary containing search parameters (genre, actor, director, year, min_rating)
            count: Number of results to return
            
        Returns:
            List of movie dictionaries with details
        """
        try:
            # Handle different types of searches based on criteria
            if 'actor' in search_criteria and search_criteria['actor']:
                return self._search_by_actor(search_criteria, count)
            elif 'director' in search_criteria and search_criteria['director']:
                return self._search_by_director(search_criteria, count)
            else:
                return self._discover_movies(search_criteria, count)
        except Exception as e:
            print(f"TMDB API error: {str(e)}")
            return [{"error": f"Failed to fetch movies: {str(e)}"}]

    def _search_by_actor(self, search_criteria: Dict[str, Any], count: int) -> List[Dict]:
        """Search movies by actor"""
        # First find the actor ID
        actor_name = search_criteria['actor']
        search_url = f"{self.base_url}/search/person"
        params = {
            "api_key": self.api_key,
            "query": actor_name
        }
        
        response = requests.get(search_url, params=params, headers=self.headers)
        data = response.json()
        
        if not data.get('results') or len(data['results']) == 0:
            return [{"error": f"Could not find actor: {actor_name}"}]
        
        # Get actor ID from the first result
        actor_id = data['results'][0]['id']
        
        # Get movies for this actor
        credits_url = f"{self.base_url}/person/{actor_id}/movie_credits"
        params = {
            "api_key": self.api_key
        }
        
        response = requests.get(credits_url, params=params, headers=self.headers)
        data = response.json()
        
        if not data.get('cast') or len(data['cast']) == 0:
            return [{"error": f"No movies found for actor: {actor_name}"}]
        
        # Filter results
        movies = self._filter_movies(data['cast'], search_criteria)
        
        # Get detailed information for each movie
        detailed_movies = self._get_detailed_movies(movies, count)
        
        # Add search metadata
        for movie in detailed_movies:
            movie['search_type'] = 'actor'
            movie['search_value'] = actor_name
        
        return detailed_movies[:count]
    
    def _search_by_director(self, search_criteria: Dict[str, Any], count: int) -> List[Dict]:
        """Search movies by director"""
        # First find the director ID
        director_name = search_criteria['director']
        search_url = f"{self.base_url}/search/person"
        params = {
            "api_key": self.api_key,
            "query": director_name
        }
        
        response = requests.get(search_url, params=params, headers=self.headers)
        data = response.json()
        
        if not data.get('results') or len(data['results']) == 0:
            return [{"error": f"Could not find director: {director_name}"}]
        
        # Get director ID from the first result
        director_id = data['results'][0]['id']
        
        # Get movies for this director
        credits_url = f"{self.base_url}/person/{director_id}/movie_credits"
        params = {
            "api_key": self.api_key
        }
        
        response = requests.get(credits_url, params=params, headers=self.headers)
        data = response.json()
        
        if not data.get('crew') or len(data['crew']) == 0:
            return [{"error": f"No movies found for director: {director_name}"}]
        
        # Filter to only directing credits
        director_movies = [movie for movie in data['crew'] if movie.get('job', '').lower() == 'director']
        
        if not director_movies:
            return [{"error": f"No movies found where {director_name} was the director"}]
        
        # Filter results
        movies = self._filter_movies(director_movies, search_criteria)
        
        # Get detailed information for each movie
        detailed_movies = self._get_detailed_movies(movies, count)
        
        # Add search metadata
        for movie in detailed_movies:
            movie['search_type'] = 'director'
            movie['search_value'] = director_name
        
        return detailed_movies[:count]

    def _discover_movies(self, search_criteria: Dict[str, Any], count: int) -> List[Dict]:
        """Discover movies based on criteria like genre, year, rating"""
        discover_url = f"{self.base_url}/discover/movie"
        params = {
            "api_key": self.api_key,
            "sort_by": "popularity.desc"  # Default sort
        }
        
        # Handle genre
        if 'genre' in search_criteria and search_criteria['genre']:
            genre_id = self._get_genre_id(search_criteria['genre'])
            if genre_id:
                params["with_genres"] = genre_id
        
        # Handle year
        if 'year' in search_criteria and search_criteria['year']:
            params["primary_release_year"] = search_criteria['year']
        
        # Handle minimum rating
        if 'min_rating' in search_criteria and search_criteria['min_rating']:
            params["vote_average.gte"] = search_criteria['min_rating']
            # Require a minimum number of votes for rating to be meaningful
            params["vote_count.gte"] = 100
            # Sort by rating if we're filtering by rating
            params["sort_by"] = "vote_average.desc"
        
        # Make the request
        response = requests.get(discover_url, params=params, headers=self.headers)
        data = response.json()
        
        if not data.get('results') or len(data['results']) == 0:
            return [{"error": "No movies found with the specified criteria"}]
        
        # Get detailed information for each movie
        detailed_movies = self._get_detailed_movies(data['results'], count)
        
        # Add search metadata
        search_type = 'genre' if 'genre' in search_criteria and search_criteria['genre'] else \
                     'year' if 'year' in search_criteria and search_criteria['year'] else 'popular'
        search_value = search_criteria.get(search_type, 'popular')
        
        for movie in detailed_movies:
            movie['search_type'] = search_type
            movie['search_value'] = search_value
        
        return detailed_movies[:count]

    def _get_genre_id(self, genre_name: str) -> Optional[int]:
        """Get genre ID from genre name"""
        genre_url = f"{self.base_url}/genre/movie/list"
        params = {
            "api_key": self.api_key
        }
        
        response = requests.get(genre_url, params=params, headers=self.headers)
        data = response.json()
        
        if not data.get('genres'):
            return None
        
        # Find the genre ID that matches the name
        for genre in data['genres']:
            if genre['name'].lower() == genre_name.lower():
                return genre['id']
            
        # Try partial matching if exact match not found
        for genre in data['genres']:
            if genre_name.lower() in genre['name'].lower():
                return genre['id']
        
        return None

    def _filter_movies(self, movies: List[Dict], search_criteria: Dict[str, Any]) -> List[Dict]:
        """Filter movie list based on search criteria"""
        filtered = movies
        
        # Apply year filter
        if 'year' in search_criteria and search_criteria['year']:
            year = str(search_criteria['year'])
            filtered = [m for m in filtered if 'release_date' in m and m['release_date'].startswith(year)]
        
        # Apply minimum rating filter
        if 'min_rating' in search_criteria and search_criteria['min_rating']:
            min_rating = float(search_criteria['min_rating'])
            filtered = [m for m in filtered if 'vote_average' in m and m['vote_average'] >= min_rating]
        
        # Sort by rating (descending)
        filtered.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
        
        return filtered

    def _get_detailed_movies(self, movies: List[Dict], count: int) -> List[Dict]:
        """Get detailed information for each movie"""
        detailed_movies = []
        
        for movie in movies[:count]:
            movie_id = movie['id']
            movie_url = f"{self.base_url}/movie/{movie_id}"
            params = {
                "api_key": self.api_key,
                "append_to_response": "credits"  # Include credits to get cast and crew
            }
            
            try:
                response = requests.get(movie_url, params=params, headers=self.headers)
                details = response.json()
                
                # Construct thumbnail URL
                poster_path = details.get('poster_path')
                thumbnail = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/150"
                
                # Extract director from crew
                director = "N/A"
                if 'credits' in details and 'crew' in details['credits']:
                    directors = [person for person in details['credits']['crew'] if person['job'] == 'Director']
                    if directors:
                        director = directors[0]['name']
                
                # Format year from release date
                year = "N/A"
                if 'release_date' in details and details['release_date']:
                    year = details['release_date'].split('-')[0]
                
                detailed_movies.append({
                    'title': details.get('title', "Unknown Title"),
                    'year': year,
                    'rating': str(details.get('vote_average', "N/A")),
                    'description': details.get('overview', "No description available"),
                    'thumbnail': thumbnail,
                    'link': f"https://www.themoviedb.org/movie/{movie_id}",
                    'director': director,
                    'runtime': details.get('runtime', "N/A"),
                    'genres': ", ".join([g['name'] for g in details.get('genres', [])])
                })
            except Exception as e:
                print(f"Error getting details for movie {movie_id}: {str(e)}")
                continue
        
        return detailed_movies


class ITunesMusicTools:
    """Tools for searching music using iTunes Search API"""
    
    def __init__(self):
        self.base_url = "https://itunes.apple.com/search"
    
    def search_music(self, search_criteria: Dict[str, Any], count: int = 10) -> List[Dict]:
        """
        Search for music based on search criteria
        
        Args:
            search_criteria: Dictionary containing search parameters (artist, genre, term)
            count: Number of results to return
            
        Returns:
            List of music dictionaries with details
        """
        try:
            # Build search query
            params = {
                "media": "music",
                "limit": min(count * 2, 200),  # Get more than needed to filter
                "country": "US"  # Default to US store
            }
            
            # Handle different search types
            if 'artist' in search_criteria and search_criteria['artist']:
                params["term"] = search_criteria['artist']
                params["attribute"] = "artistTerm"
                search_type = 'artist'
                search_value = search_criteria['artist']
            elif 'genre' in search_criteria and search_criteria['genre']:
                params["term"] = search_criteria['genre']
                params["attribute"] = "genreIndex"
                search_type = 'genre'
                search_value = search_criteria['genre']
            elif 'term' in search_criteria and search_criteria['term']:
                params["term"] = search_criteria['term']
                search_type = 'term'
                search_value = search_criteria['term']
            else:
                return [{"error": "Please provide search criteria for music (artist, genre, or term)"}]
            
            # Make the request
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if not data.get('results') or len(data['results']) == 0:
                return [{"error": f"No music found for {search_type}: {search_value}"}]
            
            # Filter and format results
            songs = self._format_results(data['results'], search_type, search_value)
            
            # Get the most relevant results and sort by popularity
            songs.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            
            return songs[:count]
            
        except Exception as e:
            print(f"iTunes API error: {str(e)}")
            return [{"error": f"Failed to fetch music: {str(e)}"}]
    
    def _format_results(self, results: List[Dict], search_type: str, search_value: str) -> List[Dict]:
        """Format API results into standardized music items"""
        songs = []
        
        for result in results:
            # Skip non-songs
            if result.get('wrapperType') != 'track' or result.get('kind') != 'song':
                continue
                
            # Create a popularity score based on price (cheaper = more popular)
            # Use track price or collection price if available
            price = result.get('trackPrice', result.get('collectionPrice', 0.99))
            popularity = 10 - min(price, 9.99)  # Higher score for lower price
            
            # Get a higher resolution artwork if available
            artwork_url = result.get('artworkUrl100', '')
            if artwork_url:
                artwork_url = artwork_url.replace('100x100', '150x150')
            
            # Modified preview URL handling
            preview_url = result.get('previewUrl', '')
            if preview_url:
                # Create HTML5 audio player embed code
                preview_url = f'<audio controls style="height:30px"><source src="{preview_url}" type="audio/mpeg"></audio>'
            
            songs.append({
                'title': result.get('trackName', 'Unknown Track'),
                'artist': result.get('artistName', 'Unknown Artist'),
                'album': result.get('collectionName', 'Unknown Album'),
                'genre': result.get('primaryGenreName', 'Unknown Genre'),
                'release_date': result.get('releaseDate', 'Unknown').split('T')[0],
                'preview_url': preview_url,
                'artwork': artwork_url,
                'track_url': result.get('trackViewUrl', ''),
                'popularity': popularity,
                'search_type': search_type,
                'search_value': search_value
            })
        
        return songs


class NewsTools:
    """Tools for fetching and summarizing news using SERP API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def fetch_news(self, search_query: str, count: int = 5) -> List[Dict]:
        """
        Fetch news articles based on search query
        
        Args:
            search_query: News topic or search term
            count: Number of news articles to return
            
        Returns:
            List of news article dictionaries
        """
        try:
            # Make request to SERP API
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": search_query + " news",
                "tbm": "nws",
                "num": count * 2  # Get more than needed to filter
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if not data.get('news_results') or len(data['news_results']) == 0:
                return [{"error": f"No news found for: {search_query}"}]
            
            # Format and filter results
            news_articles = []
            
            for article in data['news_results'][:count]:
                news_articles.append({
                    'title': article.get('title', 'Untitled Article'),
                    'source': article.get('source', 'Unknown Source'),
                    'date': article.get('date', 'Unknown Date'),
                    'link': article.get('link', '#'),
                    'thumbnail': article.get('thumbnail', 'https://via.placeholder.com/150'),
                    'snippet': article.get('snippet', 'No description available')
                })
            
            return news_articles
            
        except Exception as e:
            print(f"News API error: {str(e)}")
            return [{"error": f"Failed to fetch news: {str(e)}"}]


class GeneralSearchTools:
    """Tools for general web search queries using SERP API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def web_search(self, query: str, count: int = 10) -> Dict:
        """
        Perform a general web search
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            Dictionary with search results and knowledge graph if available
        """
        try:
            # Make request to SERP API
            params = {
                "api_key": self.api_key,
                "engine": "google",
                "q": query,
                "num": count
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            result = {
                "search_query": query,
                "knowledge_graph": None,
                "organic_results": []
            }
            
            # Extract knowledge graph if available
            if 'knowledge_graph' in data:
                result["knowledge_graph"] = {
                    "title": data['knowledge_graph'].get('title', ''),
                    "type": data['knowledge_graph'].get('type', ''),
                    "description": data['knowledge_graph'].get('description', ''),
                    "thumbnail": data['knowledge_graph'].get('thumbnail', '')
                }
            
            # Extract organic results
            if 'organic_results' in data:
                for item in data['organic_results'][:count]:
                    result["organic_results"].append({
                        "title": item.get('title', ''),
                        "link": item.get('link', ''),
                        "snippet": item.get('snippet', '')
                    })
            
            return result
            
        except Exception as e:
            print(f"Search API error: {str(e)}")
            return {"error": f"Failed to perform search: {str(e)}"}