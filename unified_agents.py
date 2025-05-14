from crewai import Agent, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict, PrivateAttr
from typing import Type
from api_tools import NewsTools, GeneralSearchTools
from langchain_google_genai import GoogleGenerativeAI
# from gemini import GeminiLLM 
# from deepseek import PegasusLLM
from langchain_openai import ChatOpenAI
# from together import Together
from langchain_together import Together
from dotenv import load_dotenv
load_dotenv("keys.env")
import os


llm=LLM(
    model="together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    # model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    api_key=os.getenv("TOGETHER_API_KEY"),
    api_base="https://api.together.xyz",
    # endpont = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
)


class MovieSearchInput(BaseModel):
    query: str = Field(..., description="Movie search query")

class MusicSearchInput(BaseModel):
    query: str = Field(..., description="Music search query")

class NewsSearchInput(BaseModel):
    search_query: str = Field(..., description="News search query")
    count: int = Field(5, description="Number of news articles to fetch")

class WebSearchInput(BaseModel):
    query: str = Field(..., description="Web search query")

# ----------------- Tool Definitions -----------------

class MovieSearchTool(BaseTool):
    name: str = "Search Movies"
    description: str = "Search for movies using Web Search"
    args_schema: Type[BaseModel] = MovieSearchInput
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _search_tools: GeneralSearchTools = PrivateAttr()

    def __init__(self, search_tools: GeneralSearchTools):
        super().__init__()
        self._search_tools = search_tools

    def _run(self, query: str) -> str:
        # Use the web search implementation for movies
        return self._search_tools.web_search(query)

class MusicSearchTool(BaseTool):
    name: str = "Search Music"
    description: str = "Search for music using Web Search"
    args_schema: Type[BaseModel] = MusicSearchInput
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _search_tools: GeneralSearchTools = PrivateAttr()

    def __init__(self, search_tools: GeneralSearchTools):
        super().__init__()
        self._search_tools = search_tools

    def _run(self, query: str) -> str:
        # Use the web search implementation for music
        return self._search_tools.web_search(query)

class NewsSearchTool(BaseTool):
    name: str = "Fetch News"
    description: str = "Fetch news articles using SERP API"
    args_schema: Type[BaseModel] = NewsSearchInput
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _news_tools: NewsTools = PrivateAttr()

    def __init__(self, news_tools: NewsTools):
        super().__init__()
        self._news_tools = news_tools

    def _run(self, search_query: str, count: int = 5) -> str:
        return self._news_tools.fetch_news(search_query, count)

class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = "Perform general web searches using SERP API"
    args_schema: Type[BaseModel] = WebSearchInput
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _search_tools: GeneralSearchTools = PrivateAttr()

    def __init__(self, search_tools: GeneralSearchTools):
        super().__init__()
        self._search_tools = search_tools

    def _run(self, query: str) -> str:
        return self._search_tools.web_search(query)

# ----------------- Unified Search Agents -----------------

class UnifiedSearchAgents:
    def __init__(self, tmdb_api_key: str, tmdb_token: str, serp_api_key: str):
        # Instead of using TMDB and iTunes tools, use the general web search tool for both movies and music.
        self.news_tools = NewsTools(serp_api_key)
        self.search_tools = GeneralSearchTools(serp_api_key)

        self.movie_search_tool = MovieSearchTool(self.search_tools)
        self.music_search_tool = MusicSearchTool(self.search_tools)
        self.news_search_tool = NewsSearchTool(self.news_tools)
        self.web_search_tool = WebSearchTool(self.search_tools)

    def create_movie_agent(self) -> Agent:
        return Agent(
            role='Movie Search Specialist',
            goal='Find high-quality movie information based on user queries',
            backstory='Expert in movie data analysis with vast knowledge of films, directors, and actors.',
            llm=llm,
            tools=[self.movie_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def create_music_agent(self) -> Agent:
        return Agent(
            role='Music Discovery Specialist',
            goal='Find and present music that matches user preferences',
            backstory='Experienced music curator with deep knowledge of artists, genres, and trends.',
            llm=llm,
            tools=[self.music_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def create_news_agent(self) -> Agent:
        return Agent(
            role='News Analyst',
            goal='Find and summarize relevant news stories',
            backstory='Seasoned journalist with experience in quickly finding, analyzing, and summarizing news across various topics.',
            llm=llm,
            tools=[self.news_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def create_search_agent(self) -> Agent:
        return Agent(
            role='Research Specialist',
            goal='Find accurate information for general queries',
            backstory='Meticulous researcher with experience in finding reliable information across various domains.',
            llm=llm,
            tools=[self.web_search_tool],
            verbose=True,
            allow_delegation=False
        )

# ----------------- Main Execution -----------------

if __name__ == '__main__':
    # Replace with your actual API keys/tokens
    TMDB_API_KEY = "your_tmdb_api_key"
    TMDB_TOKEN = "your_tmdb_token"
    SERP_API_KEY = "your_serp_api_key"

    # Instantiate the unified search agents
    unified_agents = UnifiedSearchAgents(TMDB_API_KEY, TMDB_TOKEN, SERP_API_KEY)
    
    # Example: Create a movie agent and run a sample query
    movie_agent = unified_agents.create_movie_agent()
    
    # This will now use the web search implementation.
    result = movie_agent.tools[0]._run("Inception")
    print(result)
