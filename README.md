# VIBESTA - Festival Information Hub

VIBESTA is a web application that allows users to search for festivals and get categorized details about them, including Overview information from Wikipedia, and detailed Food, History, Dress, and Culture information fetched from Google's Gemini API. The app also features a community section where users can anonymously post festival-related content.

## Features

- **Festival Information Search**: Search for festivals and get comprehensive information
- **Categorized Details**: Information organized into Overview, Food, History, Dress, and Culture categories
- **Community Posts**: Users can share festival experiences through images and videos
- **Interactive Interface**: Like and comment on community posts
- **API Cost Optimization**: MongoDB caching of festival details to reduce API calls
- **Content Moderation**: Appropriate content verification using Gemini
- **Popular Festivals**: Track and display trending festival searches
- **Responsive Design**: Works on desktop and mobile devices
- **Robust Error Handling**: Fallback content when APIs fail to provide information

## Prerequisites

- Python 3.7 or higher
- MongoDB (installed and running)
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vibesta.git
cd vibesta
```

2. Install dependencies:
```bash
pip install -r requiremnts.txt
```

3. Configure environment variables:
- Create a `.env` file in the project root
- Add the following variables:
```
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=festivalDB
SECRET_KEY=your_secret_key_for_flask
```

4. Make sure MongoDB is running on your system:
```bash
# To check if MongoDB is running
mongod --version
```

5. Run the application:
```bash
python main.py
```

6. Open your browser and go to `http://localhost:5000`

## Project Structure

- `main.py`: Main Flask application with all functionality
  - MongoDB utilities
  - Gemini API integration
  - Data fetching functions
  - Flask routes
- `static/`: Static assets
  - `style.css`: CSS styles for the application
  - `script.js`: JavaScript for interactive features
  - `uploads/`: Directory for user uploaded content
- `templates/`: HTML templates
  - `index.html`: Home page with community posts
  - `search.html`: Festival search and information display
  - `upload.html`: Post upload form
  - `festival_posts.html`: Festival-specific posts page

## Using the Application

### Searching for Festival Information

1. Click on "Search Festivals" in the navigation bar
2. Enter a festival name (e.g., Diwali, Christmas, Holi)
3. View the overview information and navigate through different tabs to explore Food, Culture, Dress, and History

### Sharing Festival Content

1. Click on "Share Experience" in the navigation bar
2. Upload an image or video from a festival
3. Add a caption that includes festival-related keywords
4. Submit your post to share with the community

### Viewing Festival-Specific Posts

1. Click on a festival name from the "Popular Festivals" sidebar
2. Browse posts specifically related to that festival
3. Like and comment on posts that interest you

## API Endpoints

VIBESTA provides API endpoints for accessing festival information programmatically:

- `/api/festivals/popular`: Get a list of popular festivals
- `/api/festival/<festival_name>/<category>`: Get specific information about a festival
  - Categories: overview, food, culture, dress, history

## Error Handling

The application includes robust error handling with fallback content:

- If Wikipedia fails to provide information, default festival data is displayed
- If APIs experience errors, Gemini generates appropriate content
- All user actions have proper error handling with helpful messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page) for festival overviews
- [Wikidata SPARQL](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service) for festival details
- [Google Gemini API](https://ai.google.dev/docs) for detailed festival information
- [Flask](https://flask.palletsprojects.com/) web framework
- [MongoDB](https://www.mongodb.com/) for data storage 