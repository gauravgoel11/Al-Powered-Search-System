from flask import Flask, render_template, request, jsonify
from unified_crewai import UnifiedSearchCrew
import os
import json
import re
from dotenv import load_dotenv


app = Flask(__name__)
# Load environment variables from .env file
load_dotenv("keys.env")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_TOKEN = os.getenv("TMDB_TOKEN")
SERP_API_KEY = os.getenv("SERP_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
# Initialize the crew
crew_manager = UnifiedSearchCrew(TMDB_API_KEY, TMDB_TOKEN, SERP_API_KEY)

def extract_content_from_crew_output(output):
    """Extract the actual content string from the CrewOutput object or string"""
    
    # If it's None, return empty string
    if output is None:
        return ""
    
    # Check if it's a dictionary with a 'result' key (from crew_manager.run)
    if isinstance(output, dict) and 'result' in output:
        # Access the CrewOutput object inside the dict
        return extract_content_from_crew_output(output['result'])
    
    # If it's already a string, return it directly
    if isinstance(output, str):
        return output
    
    # If it has a 'raw' attribute (which is the case for CrewOutput)
    if hasattr(output, "raw"):
        return output.raw
    
    # If the object has a tasks_output list
    if hasattr(output, "tasks_output") and output.tasks_output:
        # Get the raw output from the first task
        first_task = output.tasks_output[0]
        if hasattr(first_task, "raw") and first_task.raw:
            return first_task.raw
    
    # Last resort: convert to string
    return str(output)

@app.route("/", methods=["GET"])
def index():
    """Render the main page"""
    return render_template("index.html")

@app.route("/api/search", methods=["POST"])
def api_search():
    """Process search query and return results"""
    data = request.json
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "Please provide a search query"})
    
    try:
        # Process the user input using the unified crew
        result = crew_manager.run(user_input)
        
        # Extract the content and return it directly
        content = extract_content_from_crew_output(result)
        
        # Return the result in a simplified format
        return jsonify({
            "type": "general",
            "content": content
        })
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"})

# Movie-specific endpoint
@app.route("/api/movie", methods=["POST"])
def api_movie():
    """Search for movies"""
    data = request.json
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "Please provide a movie search query"})
    
    try:
        # Process the movie search
        result = crew_manager.run_movie_search(user_input)
        
        # Extract the content 
        content = extract_content_from_crew_output(result)
        
        # Return the result in a simplified format
        return jsonify({
            "type": "movie",
            "content": content
        })
    except Exception as e:
        print(f"Error in movie search: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"})

# Music-specific endpoint
@app.route("/api/music", methods=["POST"])
def api_music():
    """Search for music"""
    data = request.json
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "Please provide a music search query"})
    
    try:
        # Process the music search
        result = crew_manager.run_music_search(user_input)
        
        # Extract the content
        content = extract_content_from_crew_output(result)
        
        # Return the result in a simplified format
        return jsonify({
            "type": "music",
            "content": content
        })
    except Exception as e:
        print(f"Error in music search: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"})

# News-specific endpoint
@app.route("/api/news", methods=["POST"])
def api_news():
    """Search for news"""
    data = request.json
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "Please provide a news search query"})
    
    try:
        # Process the news search
        result = crew_manager.run_news_search(user_input)
        
        # Extract the content
        content = extract_content_from_crew_output(result)
        
        # Return the result in a simplified format  
        return jsonify({
            "type": "news",
            "content": content
        })
    except Exception as e:
        print(f"Error in news search: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"})

# General search endpoint
@app.route("/api/general", methods=["POST"])
def api_general():
    """General web search"""
    data = request.json
    user_input = data.get("user_input", "")
    
    if not user_input:
        return jsonify({"error": "Please provide a search query"})
    
    try:
        # Process the general search
        result = crew_manager.run_general_search(user_input)
        
        # Extract the content
        content = extract_content_from_crew_output(result)
        
        # Return the result in a simplified format
        return jsonify({
            "type": "general",
            "content": content
        })
    except Exception as e:
        print(f"Error in general search: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)