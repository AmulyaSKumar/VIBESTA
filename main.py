import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from pymongo import MongoClient
import os
from bson import ObjectId
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.secret_key = os.getenv('SECRET_KEY', 'secret_key')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure the Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'festivalDB')

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
festival_info_collection = db['festival_info']
posts_collection = db['posts']

# API URLs
WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

# List of festival keywords for post validation
FESTIVAL_KEYWORDS = ["festival", "vibe", "diwali", "eid", "holi", "christmas", "pongal", "event", "celebration", "carnival", "fair"]

# Default festival information as fallback
DEFAULT_FESTIVALS = {
    "diwali": {
        "title": "Diwali",
        "description": "Diwali, also known as the Festival of Lights, is one of the major festivals celebrated by Hindus, Jains, and Sikhs. The festival usually lasts five days and is celebrated during the Hindu lunisolar month Kartika. One of the most popular festivals of Hinduism, Diwali symbolizes the spiritual victory of light over darkness, good over evil, and knowledge over ignorance.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Diwali_Diya.jpg/800px-Diwali_Diya.jpg"
    },
    "christmas": {
        "title": "Christmas",
        "description": "Christmas is an annual festival commemorating the birth of Jesus Christ, observed primarily on December 25 as a religious and cultural celebration among billions of people around the world. A feast central to the Christian liturgical year, it is preceded by the season of Advent and initiates the season of Christmastide, which traditionally in the West lasts twelve days and culminates on Twelfth Night.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Christmastree_1.jpg/800px-Christmastree_1.jpg"
    },
    "holi": {
        "title": "Holi",
        "description": "Holi is a popular ancient Indian festival, also known as the 'Festival of Love', the 'Festival of Colours' and the 'Festival of Spring'. The festival celebrates the eternal and divine love of Radha Krishna. It also signifies the triumph of good over evil, as it celebrates the victory of Lord Vishnu as Narasimha Narayana over Hiranyakashipu.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Holi_celebration_at_Barsana.jpg/800px-Holi_celebration_at_Barsana.jpg"
    },
    "eid": {
        "title": "Eid al-Fitr",
        "description": "Eid al-Fitr, also called the 'Festival of Breaking the Fast', is a religious holiday celebrated by Muslims worldwide that marks the end of Ramadan, the Islamic holy month of fasting. The religious Eid is a single day during which Muslims are not permitted to fast. The holiday celebrates the conclusion of the 29 or 30 days of dawn-to-sunset fasting during the entire month of Ramadan.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Eid_prayer.jpg/800px-Eid_prayer.jpg"
    }
}

#---------- MongoDB UTILITY FUNCTIONS ----------#
def get_cached_festival_data(festival_name, category):
    """
    Retrieve cached festival data from MongoDB.
    
    Args:
        festival_name (str): Name of the festival
        category (str): Category to retrieve (overview, food, history, dress, culture)
        
    Returns:
        dict: Festival data if found and not expired, None otherwise
    """
    try:
        # Define the cache expiration time (30 days)
        expiration_date = datetime.now() - timedelta(days=30)
        
        # Query for the festival data
        query = {
            "festival_name": festival_name.lower(),
            "category": category.lower(),
            "timestamp": {"$gt": expiration_date}
        }
        
        result = festival_info_collection.find_one(query)
        
        return result
    except Exception as e:
        print(f"Error retrieving cached data: {str(e)}")
        return None

def cache_festival_data(festival_name, category, data):
    """
    Cache festival data in MongoDB.
    
    Args:
        festival_name (str): Name of the festival
        category (str): Category of the data (overview, food, history, dress, culture)
        data (dict): The festival data to cache
        
    Returns:
        bool: True if successfully cached, False otherwise
    """
    try:
        # Add timestamp and normalize festival name
        document = {
            "festival_name": festival_name.lower(),
            "category": category.lower(),
            "data": data,
            "timestamp": datetime.now()
        }
        
        # First, check if a document already exists and update it if it does
        query = {
            "festival_name": festival_name.lower(),
            "category": category.lower()
        }
        
        festival_info_collection.update_one(
            query,
            {"$set": document},
            upsert=True
        )
        
        return True
    
    except Exception as e:
        print(f"Error caching festival data: {str(e)}")
        return False

def get_popular_festivals():
    """
    Get a list of popular festivals based on search frequency.
    
    Returns:
        list: List of dictionaries containing festival names and search counts
    """
    try:
        pipeline = [
            {"$group": {"_id": "$festival_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        results = list(festival_info_collection.aggregate(pipeline))
        festivals = [{"name": item["_id"], "count": item["count"]} for item in results]
        
        # If no festivals found in database, return default popular festivals
        if not festivals:
            return [
                {"name": "diwali", "count": 100},
                {"name": "christmas", "count": 90},
                {"name": "holi", "count": 80},
                {"name": "eid", "count": 70}
            ]
            
        return festivals
    except Exception as e:
        print(f"Error getting popular festivals: {str(e)}")
        # Return default popular festivals on error
        return [
            {"name": "diwali", "count": 100},
            {"name": "christmas", "count": 90},
            {"name": "holi", "count": 80},
            {"name": "eid", "count": 70}
        ]

def get_festival_posts(festival_name=None):
    """
    Get posts related to a specific festival or all festival posts.
    
    Args:
        festival_name (str, optional): Name of the festival to filter by
        
    Returns:
        list: List of posts
    """
    try:
        query = {}
        if festival_name:
            # Search for the festival name in the caption (case-insensitive)
            query = {"caption": {"$regex": festival_name, "$options": "i"}}
        
        posts = list(posts_collection.find(query).sort("_id", -1))
        return posts
    except Exception as e:
        print(f"Error retrieving posts: {str(e)}")
        return []

#---------- GEMINI API UTILITY FUNCTIONS ----------#
def get_festival_details_from_gemini(festival_name, category):
    """
    Fetch festival details from Gemini API based on category.
    
    Args:
        festival_name (str): Name of the festival
        category (str): One of 'food', 'history', 'dress', 'culture'
        
    Returns:
        dict: Dictionary containing title and description
    """
    try:
        # Create a prompt based on the category
        if category == 'food':
            prompt = f"Tell me about the traditional foods associated with {festival_name} festival. Provide detailed information about dishes, ingredients, significance, and how they're prepared."
        elif category == 'history':
            prompt = f"Explain the historical origins and evolution of {festival_name} festival. When did it begin, what historical events shaped it, and how has it changed over time?"
        elif category == 'dress':
            prompt = f"Describe the traditional clothing and attire worn during {festival_name} festival. What are the specific garments, colors, patterns, and their cultural significance?"
        elif category == 'culture':
            prompt = f"Explain the cultural significance and practices of {festival_name} festival. What rituals, customs, beliefs, and community activities are associated with it?"
        else:
            return {"title": category.title(), "description": "No information available for this category."}
        
        # Generate content using Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Process and return the response
        if response:
            return {
                "title": f"{category.title()} of {festival_name}",
                "description": response.text
            }
        else:
            return {"title": category.title(), "description": "Could not generate information for this category."}
    except Exception as e:
        print(f"Error using Gemini API: {str(e)}")
        # Return default information based on category
        default_descriptions = {
            'food': f"Traditional foods are an important part of {festival_name} celebrations. They often include special dishes prepared only during this festival time.",
            'history': f"{festival_name} has deep historical roots and has evolved over centuries, becoming an important cultural tradition.",
            'dress': f"Special attire is often worn during {festival_name} celebrations, with colors and styles that hold cultural significance.",
            'culture': f"{festival_name} is rich in cultural traditions, including various customs, rituals, and community activities."
        }
        
        return {
            "title": f"{category.title()} of {festival_name}",
            "description": default_descriptions.get(category, f"Information about {category} of {festival_name} is currently unavailable.")
        }

def is_appropriate_content(text):
    """
    Check if the content is appropriate using Gemini's content moderation.
    
    Args:
        text (str): Text to be checked
        
    Returns:
        bool: True if content is appropriate, False otherwise
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Analyze the following content and determine if it's appropriate for a family-friendly festival information website.
        Return ONLY "APPROPRIATE" or "INAPPROPRIATE".
        
        Content: {text}
        """
        
        response = model.generate_content(prompt)
        
        if response and "APPROPRIATE" in response.text.upper():
            return True
        return False
        
    except Exception as e:
        print(f"Error in content moderation: {str(e)}")
        # For safety, if there's an error, check if text contains common inappropriate terms
        inappropriate_terms = ["porn", "sex", "nude", "naked", "obscene", "violent", "kill", "drug", "abuse"]
        for term in inappropriate_terms:
            if term in text.lower():
                return False
        # If no obvious inappropriate terms, allow it
        return True

#---------- FESTIVAL DATA FETCHING FUNCTIONS ----------#
def get_wikipedia_info(festival_name):
    """Fetch Wikipedia summary for the festival (overview, history)."""
    try:
        response = requests.get(WIKI_API_URL + festival_name.replace(" ", "_"))
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "description": data.get("extract"),
                "image": data.get("thumbnail", {}).get("source"),
                "wiki_url": data.get("content_urls", {}).get("desktop", {}).get("page"),
            }
            
        # Try to get default information
        festival_key = festival_name.lower()
        if festival_key in DEFAULT_FESTIVALS:
            return DEFAULT_FESTIVALS[festival_key]
        
        # If nothing found, use Gemini to generate overview
        return get_festival_details_from_gemini(festival_name, "overview")
    except Exception as e:
        print(f"Error fetching Wikipedia info: {str(e)}")
        # Try to return default festival info
        festival_key = festival_name.lower()
        if festival_key in DEFAULT_FESTIVALS:
            return DEFAULT_FESTIVALS[festival_key]
        
        # Generate a basic overview
        return {
            "title": festival_name.title(),
            "description": f"{festival_name.title()} is a festival celebrated in various parts of the world. It involves cultural traditions, special foods, and community gatherings.",
            "image": None
        }

def get_wikidata_info(festival_name, category):
    """Fetch cultural details (food, dress, history) from Wikidata."""
    try:
        # Define property mappings in Wikidata
        property_map = {
            "history": "P2184",  # Significant event
            "food": "P279",  # Type of food
            "dress": "P1552",  # Traditional clothing
            "culture": "P2596",  # Culture
        }

        if category not in property_map:
            return {"title": category.title(), "description": "No information found."}

        query = f"""
        SELECT ?itemLabel WHERE {{
          ?festival rdfs:label "{festival_name}"@en.
          ?festival wdt:{property_map[category]} ?item.
          ?item rdfs:label ?itemLabel.
          FILTER (lang(?itemLabel) = 'en')
        }}
        """

        sparql = SPARQLWrapper(WIKIDATA_SPARQL_URL)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert().get("results", {}).get("bindings", [])

        if results:
            details = [result["itemLabel"]["value"] for result in results]
            return {
                "title": category.title(),
                "description": ", ".join(details),
            }

        # If no results, try Gemini
        return get_festival_details_from_gemini(festival_name, category)
    except Exception as e:
        print(f"Error fetching Wikidata info: {str(e)}")
        # Try Gemini as fallback
        return get_festival_details_from_gemini(festival_name, category)

def search_festival_data(festival_name, category):
    """
    Try MongoDB cache first, then external APIs for festival information.
    Caches the results in MongoDB for future use.
    """
    try:
        # First, check if we have cached data
        cached_data = get_cached_festival_data(festival_name, category)
        if cached_data:
            return cached_data["data"]

        # If no cached data, proceed to fetch from APIs
        result = None
        
        if category == "overview":
            result = get_wikipedia_info(festival_name)
        else:
            # Try Wikidata first
            wikidata_result = get_wikidata_info(festival_name, category)
            if wikidata_result and wikidata_result["description"] != "No information found.":
                result = wikidata_result
            else:
                # If Wikidata fails, try Gemini
                gemini_result = get_festival_details_from_gemini(festival_name, category)
                result = gemini_result

        # Cache the result if it's valid
        if result:
            cache_festival_data(festival_name, category, result)
            return result
        
        # If everything fails, return a default response
        return {
            "title": f"{category.title()} of {festival_name.title()}",
            "description": f"Information about {category} for {festival_name} is currently unavailable."
        }
    except Exception as e:
        print(f"Error in search festival data: {str(e)}")
        # Last resort fallback
        return {
            "title": f"{category.title()} of {festival_name.title()}",
            "description": f"Information about {category} for {festival_name} is currently unavailable due to a technical issue."
        }

#---------- FLASK ROUTES ----------#
@app.route("/")
def index():
    try:
        posts = list(posts_collection.find())
        # Get popular festivals for the sidebar
        popular_festivals = get_popular_festivals()
        return render_template('index.html', posts=posts, popular_festivals=popular_festivals)
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        flash("An error occurred while loading the homepage. Please try again.", "error")
        return render_template('index.html', posts=[], popular_festivals=[])

@app.route("/search", methods=["GET", "POST"])
def search_festival():
    festival_info = None
    extra_info = {}
    festival_name = None

    try:
        if request.method == "POST":
            festival_name = request.form.get("festival_name")
        elif request.method == "GET" and request.args.get("q"):
            festival_name = request.args.get("q")
            
        if festival_name:
            # Load overview data first
            festival_info = search_festival_data(festival_name, "overview")
            
            # Then get additional information in each category
            for category in ["food", "culture", "dress", "history"]:
                extra_info[category] = search_festival_data(festival_name, category)

        # Get popular festivals for the sidebar
        popular_festivals = get_popular_festivals()
        
        if festival_name and not festival_info:
            flash(f"Could not find information about '{festival_name}'. Please try another festival name.", "error")
                
        return render_template("search.html", 
                              festival_info=festival_info, 
                              extra_info=extra_info, 
                              popular_festivals=popular_festivals,
                              festival_name=festival_name)
    except Exception as e:
        print(f"Error in search route: {str(e)}")
        flash("An error occurred while searching. Please try again.", "error")
        return render_template("search.html", 
                              festival_info=None, 
                              extra_info={}, 
                              popular_festivals=get_popular_festivals(),
                              festival_name=festival_name)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            # Get caption/story
            caption = request.form.get('caption', '').strip()
            
            # Check if we have either a file or caption (at least one is required)
            has_file = 'file' in request.files and request.files['file'].filename != ''
            has_caption = caption != ''
            
            if not has_file and not has_caption:
                flash("Please provide either a media file or a festival story.", "error")
                return redirect(request.url)
            
            # Check if caption is provided and appropriate
            if has_caption:
                # Check if festival story is appropriate if provided
                if not is_appropriate_content(caption):
                    flash("Your festival story contains inappropriate content. Please revise it.", "error")
                    return redirect(request.url)
                
                # Check for festival keywords if caption is provided
                if not any(keyword in caption.lower() for keyword in FESTIVAL_KEYWORDS):
                    flash("Error: Your festival story must contain festival-related keywords.", "error")
                    return redirect('/upload')

            # Process file if it exists
            filename = None
            if has_file:
                file = request.files['file']
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create post
            post = {
                "caption": caption if has_caption else "Festival moment shared without a story",
                "filename": filename,
                "likes": 0, 
                "comments": [], 
                "timestamp": datetime.now(),
                "post_id": str(ObjectId())  # Generate a unique ID for each post
            }
            
            # Insert the post
            result = posts_collection.insert_one(post)
            
            flash("Your festival moment has been shared successfully!", "success")
            return redirect('/')
        except Exception as e:
            print(f"Error uploading: {str(e)}")
            flash("An error occurred while sharing your festival moment. Please try again.", "error")
            return redirect('/upload')
            
    return render_template('upload.html')

@app.route('/post/<post_id>')
def view_post(post_id):
    """View a single post and its details."""
    try:
        post = posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            flash("Post not found.", "error")
            return redirect('/')
            
        popular_festivals = get_popular_festivals()
        return render_template('view_post.html', post=post, popular_festivals=popular_festivals)
    except Exception as e:
        print(f"Error viewing post: {str(e)}")
        flash("Could not load the post. Please try again.", "error")
        return redirect('/')

@app.route('/like/<post_id>', methods=['POST'])
def like(post_id):
    try:
        posts_collection.update_one({'_id': ObjectId(post_id)}, {'$inc': {'likes': 1}})
        return redirect(request.referrer or '/')
    except Exception as e:
        print(f"Error liking post: {str(e)}")
        flash("Could not like the post. Please try again.", "error")
        return redirect('/')

@app.route('/comment/<post_id>', methods=['POST'])
def comment(post_id):
    try:
        comment_text = request.form['comment']
        
        # Check if comment is appropriate
        if not is_appropriate_content(comment_text):
            flash("Your comment contains inappropriate content. Please revise it.", "error")
            return redirect(request.referrer or '/')
            
        posts_collection.update_one({'_id': ObjectId(post_id)}, {'$push': {'comments': comment_text}})
        return redirect(request.referrer or '/')
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        flash("Could not add your comment. Please try again.", "error")
        return redirect('/')

@app.route('/festival/<festival_name>')
def festival_posts(festival_name):
    """Display posts related to a specific festival."""
    try:
        posts = get_festival_posts(festival_name)
        festival_info = search_festival_data(festival_name, "overview")
        return render_template('festival_posts.html', 
                            festival_name=festival_name, 
                            posts=posts, 
                            festival_info=festival_info)
    except Exception as e:
        print(f"Error loading festival posts: {str(e)}")
        flash(f"Could not load posts for {festival_name}. Please try again.", "error")
        return redirect('/')

@app.route('/api/festivals/popular')
def api_popular_festivals():
    """API endpoint for popular festivals."""
    try:
        popular_festivals = get_popular_festivals()
        return jsonify(popular_festivals)
    except Exception as e:
        print(f"Error in API: {str(e)}")
        return jsonify({"error": "Could not retrieve popular festivals"}), 500

@app.route('/api/festival/<festival_name>/<category>')
def api_festival_info(festival_name, category):
    """API endpoint for festival information."""
    try:
        if category not in ["overview", "food", "culture", "dress", "history"]:
            return jsonify({"error": "Invalid category"}), 400
            
        festival_data = search_festival_data(festival_name, category)
        return jsonify(festival_data)
    except Exception as e:
        print(f"Error in API: {str(e)}")
        return jsonify({"error": "Could not retrieve festival information"}), 500

if __name__ == "__main__":
    app.run(debug=True)
