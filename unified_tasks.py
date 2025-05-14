from crewai import Task

class UnifiedSearchTasks:
    """Tasks for different types of searches"""
    
    def movie_search_task(self, agent, search_criteria, count):
        """Task for searching movies using web search"""
        # Create a human-readable description of the search criteria
        search_desc = []
        if 'genre' in search_criteria:
            search_desc.append(f"genre: {search_criteria['genre']}")
        if 'actor' in search_criteria:
            search_desc.append(f"actor: {search_criteria['actor']}")
        if 'director' in search_criteria:
            search_desc.append(f"director: {search_criteria['director']}")
        if 'year' in search_criteria:
            search_desc.append(f"year: {search_criteria['year']}")
        if 'min_rating' in search_criteria:
            search_desc.append(f"minimum rating: {search_criteria['min_rating']}")
            
        search_description = ", ".join(search_desc) if search_desc else "popular movies"
        
        return Task(
            description=f'''
            Your task is to retrieve the top {count} movies matching the following criteria:
            {search_description}
            
            Use the web_search tool with these parameters:
            - query: {search_criteria}
            - count: {count}
            
            Format each movie as:
            
            - **Title:** [Movie Title] ([Year])
            - **Rating:** [Rating]/10
            - **Director:** [Director]
            - **Genres:** [Genres]
            - **Runtime:** [Runtime] minutes
            - **Description:** [Description]
            - **Thumbnail:** ![Thumbnail](thumbnail_url)
            - **Link:** [Link](movie_link)
            
            Ensure all fields are properly populated for each movie.
            ''',
            expected_output=f"A list of {count} top movies matching {search_description} with complete details in the specified format",
            agent=agent
        )

    def music_search_task(self, agent, search_criteria, count):
        """Task for searching music using web search"""
        # Create a human-readable description of the search criteria
        search_desc = []
        if 'artist' in search_criteria:
            search_desc.append(f"artist: {search_criteria['artist']}")
        if 'genre' in search_criteria:
            search_desc.append(f"genre: {search_criteria['genre']}")
        if 'term' in search_criteria:
            search_desc.append(f"term: {search_criteria['term']}")
            
        search_description = ", ".join(search_desc) if search_desc else "popular music"
        
        return Task(
            description=f'''
            Your task is to retrieve the top {count} songs matching the following criteria:
            {search_description}
            
            Use the web_search tool with these parameters:
            - query: {search_criteria}
            - count: {count}
            
            Format each song as:
            
            - **Title:** [Song Title]
            - **Artist:** [Artist Name]
            - **Album:** [Album Name]
            - **Genre:** [Genre]
            - **Release Date:** [Release Date]
            - **Preview:** [Audio Player](preview_url)
            - **Artwork:** ![Album Cover](artwork_url)
            - **Link:** [Listen Link](track_url)
            
            Ensure all fields are properly populated for each song.
            ''',
            expected_output=f"A list of {count} songs matching {search_description} with complete details in the specified format",
            agent=agent
        )

    def news_search_task(self, agent, search_query, count):
        """Task for searching and summarizing news"""
        return Task(
            description=f'''
            Your task is to search for and summarize the latest news about "{search_query}".
            
            Use the fetch_news tool with these parameters:
            - search_query: "{search_query}"
            - count: {count}
            
            For each news article:
            1. Summarize the key points in 2-3 sentences
            2. Format each article as:
            
            ## [Article Title]
            **Source:** [Source Name] | **Date:** [Publication Date]
            
            [Your 2-3 sentence summary]
            
            **Link:** [Read More](article_link)
            
            Ensure all articles are recent and relevant to the search query.
            Provide a brief overall summary of the topic at the beginning.
            ''',
            expected_output=f"A summary of {count} recent news articles about '{search_query}' with links to the original sources",
            agent=agent
        )

    def general_search_task(self, agent, query):
        """Task for general web search queries"""
        return Task(
            description=f'''
            Your task is to perform a web search for "{query}" and provide a comprehensive answer.
            
            Use the web_search tool with these parameters:
            - query: "{query}"
            - count: 10
            
            Based on the search results:
            1. Provide a direct answer to the query (2-3 paragraphs)
            2. Include any factual information from the knowledge graph if available
            3. Cite your sources by including links to relevant websites
            4. Format your response in a clear, readable manner
            
            Ensure your answer is accurate, relevant, and to the point.
            ''',
            expected_output=f"A comprehensive answer to the query '{query}' with citations to relevant sources",
            agent=agent
        )
