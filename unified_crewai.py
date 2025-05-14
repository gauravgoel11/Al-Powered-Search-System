from crewai import Crew
from unified_agents import UnifiedSearchAgents
from unified_tasks import UnifiedSearchTasks
import json
import re

class UnifiedSearchCrew:
    def __init__(self, tmdb_api_key, tmdb_token, serp_api_key):
        self.agents = UnifiedSearchAgents(tmdb_api_key, tmdb_token, serp_api_key)
        self.tasks = UnifiedSearchTasks()
        
        # API keys and tokens for direct usage
        self.tmdb_api_key = tmdb_api_key
        self.tmdb_token = tmdb_token
        self.serp_api_key = serp_api_key

    def determine_query_type(self, user_input):
        """Determine the type of query based on user input"""
        # Movie patterns
        movie_keywords = ["movie", "film", "director", "actor", "actress", "genre", "rating", "imdb", "cinema"]
        
        # Music patterns
        music_keywords = ["song", "music", "artist", "singer", "album", "track", "playlist", "band", "listen"]
        
        # News patterns
        news_keywords = ["news", "latest", "update", "headline", "report", "article", "journalist", "current events"]
        
        # Count keyword occurrences
        movie_count = sum(1 for keyword in movie_keywords if keyword.lower() in user_input.lower())
        music_count = sum(1 for keyword in music_keywords if keyword.lower() in user_input.lower())
        news_count = sum(1 for keyword in news_keywords if keyword.lower() in user_input.lower())
        
        # Determine primary search type
        if "news" in user_input.lower() or news_count > max(movie_count, music_count):
            return "news"
        elif any(term in user_input.lower() for term in ["song", "music", "artist", "singer"]) or music_count > movie_count:
            return "music"
        elif any(term in user_input.lower() for term in ["movie", "film", "director", "actor"]) or movie_count > 0:
            return "movie"
        else:
            return "general"

    def parse_movie_query(self, user_input):
        """Extract movie search criteria from user input"""
        # Patterns for different search criteria
        genre_pattern = r"(comedy|sci-fi|horror|action|drama|romance|thriller|adventure|fantasy|animation|documentary|musical|western|crime|mystery|biography|family|war|history|sport)"
        count_pattern = r"(?:top|best)\s+(\d+)"
        actor_pattern = r"(?:actor|star|starring|with|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
        year_pattern = r"(?:from|in|year)\s+(\d{4})"
        director_pattern = r"(?:direct(?:ed|or)|by director)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
        rating_pattern = r"(?:rating|rated)\s+(?:above|over|higher than)\s+(\d(?:\.\d)?)"
        
        # Extract search parameters
        genre_match = re.search(genre_pattern, user_input, re.IGNORECASE)
        count_match = re.search(count_pattern, user_input, re.IGNORECASE)
        actor_match = re.search(actor_pattern, user_input, re.IGNORECASE)
        year_match = re.search(year_pattern, user_input)
        director_match = re.search(director_pattern, user_input, re.IGNORECASE)
        rating_match = re.search(rating_pattern, user_input, re.IGNORECASE)
        
        # Build search criteria dictionary
        search_criteria = {}
        
        if genre_match:
            search_criteria['genre'] = genre_match.group(1).lower()
        
        # Default count to 5 if not specified
        count = int(count_match.group(1)) if count_match else 5
        
        if actor_match:
            search_criteria['actor'] = actor_match.group(1)
        
        if year_match:
            search_criteria['year'] = year_match.group(1)
        
        if director_match:
            search_criteria['director'] = director_match.group(1)
        
        if rating_match:
            search_criteria['min_rating'] = float(rating_match.group(1))
        
        # Handle direct name searches without keywords (assumes first capitalized name is an actor)
        if not any(key in search_criteria for key in ['genre', 'actor', 'director']):
            name_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b"
            name_matches = re.findall(name_pattern, user_input)
            if name_matches:
                # Assume first name is an actor if no other context
                search_criteria['actor'] = name_matches[0]
        
        return search_criteria, count

    def parse_music_query(self, user_input):
        """Extract music search criteria from user input"""
        # Patterns for different search criteria
        genre_pattern = r"(pop|rock|hip hop|rap|jazz|blues|country|classical|electronic|reggae|folk|metal|punk|r&b|soul|disco|indie|alternative|punjabi|hindi)"
        count_pattern = r"(?:top|best)\s+(\d+)"
        artist_pattern = r"(?:artist|singer|by|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
        term_pattern = r"(?:about|related to|on)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})"
        
        # Extract search parameters
        genre_match = re.search(genre_pattern, user_input, re.IGNORECASE)
        count_match = re.search(count_pattern, user_input, re.IGNORECASE)
        artist_match = re.search(artist_pattern, user_input, re.IGNORECASE)
        term_match = re.search(term_pattern, user_input, re.IGNORECASE)
        
        # Build search criteria dictionary
        search_criteria = {}
        
        if genre_match:
            search_criteria['genre'] = genre_match.group(1).lower()
        
        # Default count to 5 if not specified
        count = int(count_match.group(1)) if count_match else 5
        
        if artist_match:
            search_criteria['artist'] = artist_match.group(1)
        
        if term_match:
            search_criteria['term'] = term_match.group(1)
        
        # Handle direct searches for artist names
        if not search_criteria:
            name_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b"
            name_matches = re.findall(name_pattern, user_input)
            if name_matches:
                search_criteria['artist'] = name_matches[0]
                
        # If no specific criteria found, use the whole query as a general search term
        if not search_criteria:
            search_criteria['term'] = user_input
        
        return search_criteria, count

    def parse_news_query(self, user_input):
        """Extract news search query from user input"""
        # Extract count if specified
        count_pattern = r"(?:top|latest|recent)\s+(\d+)"
        count_match = re.search(count_pattern, user_input, re.IGNORECASE)
        count = int(count_match.group(1)) if count_match else 5
        
        # Remove common prefixes to get the actual search topic
        prefixes = [
            r"^(?:get|find|show|tell me about|search for|what's new in|latest news on|updates on|news about)\s+",
            r"^(?:the latest|recent|current)\s+(?:news|updates|articles|stories|reports)\s+(?:about|on|regarding|concerning)\s+"
        ]
        
        cleaned_query = user_input
        for prefix in prefixes:
            cleaned_query = re.sub(prefix, "", cleaned_query, flags=re.IGNORECASE)
        
        return cleaned_query, count

    def run(self, user_input):
        """Process user input and execute appropriate search"""
        # Determine the type of query
        query_type = self.determine_query_type(user_input)
        
        if query_type == "movie":
            return self.run_movie_search(user_input)
        elif query_type == "music":
            return self.run_music_search(user_input)
        elif query_type == "news":
            return self.run_news_search(user_input)
        else:
            return self.run_general_search(user_input)
    
    def run_movie_search(self, user_input):
        """Run a movie search based on user input"""
        # Parse movie search criteria
        search_criteria, count = self.parse_movie_query(user_input)
        
        # Create movie agent
        movie_agent = self.agents.create_movie_agent()
        
        # Create task
        movie_task = self.tasks.movie_search_task(movie_agent, search_criteria, count)
        
        # Create crew
        crew = Crew(
            agents=[movie_agent],
            tasks=[movie_task],
            verbose=True
        )
        
        # Run the crew
        try:
            result = crew.kickoff()
            # The result here is a CrewOutput object, which isn't JSON serializable
            # But we'll handle the conversion in the API endpoint
            return {
                "type": "movie", 
                "result": result,  # This will be processed by extract_content_from_crew_output
                "search_criteria": search_criteria
            }
        except Exception as e:
            return {"type": "movie", "error": str(e), "search_criteria": search_criteria}
    
    def run_music_search(self, user_input):
        """Run a music search based on user input"""
        # Parse music search criteria
        search_criteria, count = self.parse_music_query(user_input)
        
        # Create music agent
        music_agent = self.agents.create_music_agent()
        
        # Create task
        music_task = self.tasks.music_search_task(music_agent, search_criteria, count)
        
        # Create crew
        crew = Crew(
            agents=[music_agent],
            tasks=[music_task],
            verbose=True
        )
        
        # Run the crew
        try:
            result = crew.kickoff()
            return {"type": "music", "result": result, "search_criteria": search_criteria}
        except Exception as e:
            return {"type": "music", "error": str(e), "search_criteria": search_criteria}
    
    def run_news_search(self, user_input):
        """Run a news search based on user input"""
        # Parse news search query
        search_query, count = self.parse_news_query(user_input)
        
        # Create news agent
        news_agent = self.agents.create_news_agent()
        
        # Create task
        news_task = self.tasks.news_search_task(news_agent, search_query, count)
        
        # Create crew
        crew = Crew(
            agents=[news_agent],
            tasks=[news_task],
            verbose=True
        )
        
        # Run the crew
        try:
            result = crew.kickoff()
            return {"type": "news", "result": result, "search_query": search_query}
        except Exception as e:
            return {"type": "news", "error": str(e), "search_query": search_query}
    
    def run_general_search(self, user_input):
        """Run a general web search based on user input"""
        # Create search agent
        search_agent = self.agents.create_search_agent()
        
        # Create task
        search_task = self.tasks.general_search_task(search_agent, user_input)
        
        # Create crew
        crew = Crew(
            agents=[search_agent],
            tasks=[search_task],
            verbose=True
        )
        
        # Run the crew
        try:
            result = crew.kickoff()
            return {"type": "general", "result": result, "query": user_input}
        except Exception as e:
            return {"type": "general", "error": str(e), "query": user_input}