import random
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import OpenAI

# Load environment variables for sensitive information
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection parameters
DB_CONFIG = {
    'user': 'gonc',
    'host': 'svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com',
    'port': 3333,
    'password': 'cAFjKuRtxj1EpZU4Ka3UHKrMEVqxybAQ',
    'database': 'f1hub',
    'auth_plugin': 'mysql_native_password'
}

def driver_nationality(driver_name):
    """
    Returns the nationality for a given driver name.
    
    Args:
        driver_name (str): The name of the F1 driver
    
    Returns:
        str: The nationality of the driver
    """
    if not driver_name:
        return "Unknown"
    
    nationality_map = {
        "Lewis Hamilton": "British",
        "Max Verstappen": "Dutch",
        "Charles Leclerc": "Monegasque",
        "Sebastian Vettel": "German",
        "Fernando Alonso": "Spanish",
        "Lando Norris": "British",
        "Carlos Sainz": "Spanish",
        "Oscar Piastri": "Australian",
        "Yuki Tsunoda": "Japanese",
        "George Russell": "British",
        "Jack Doohan": "Australian",
        "Gabriel Bortoleto": "Brazilian",
        "Liam Lawson": "New Zealander",
        "Pierre Gasly": "French",
        "Esteban Ocon": "French",
        "Lance Stroll": "Canadian",
        "Oliver Bearman": "British",
        "Isack Hadjar": "French",
        "Andrea Kimi Antonelli": "Italian",
        "Kimi Antonelli": "Italian",
        "Nico Hülkenberg": "German",
        "Nico Hulkenberg": "German",
        "Sergio Pérez": "Mexican",
        "Sergio Perez": "Mexican",
        "Valtteri Bottas": "Finnish",
        "Alexander Albon": "Thai",
        "Logan Sargeant": "American",
        "Kevin Magnussen": "Danish",
        "Guanyu Zhou": "Chinese",
        "Franco Colapinto": "Argentinian",
        "Daniel Ricciardo": "Australian"
    }
    
    return nationality_map.get(driver_name, "Unknown")


def get_nationality_code(nationality):
    """
    Returns the country code for a given nationality.
    
    Args:
        nationality (str): The nationality
    
    Returns:
        str: The two-letter country code
    """
    if not nationality:
        return "unknown"
    
    code_map = {
        "Dutch": "nl",
        "British": "gb",
        "Monegasque": "mc",
        "Spanish": "es",
        "Australian": "au",
        "Mexican": "mx",
        "Finnish": "fi",
        "Canadian": "ca",
        "Thai": "th",
        "Japanese": "jp",
        "French": "fr",
        "Danish": "dk",
        "German": "de",
        "American": "us",
        "Chinese": "cn",
        "Italian": "it",
        "Brazilian": "br",
        "New Zealander": "nz",
        "Argentinian": "ar"
    }
    
    return code_map.get(nationality, "unknown")


def get_team_color(team_name):
    """
    Get default team color for a given team name.
    
    Args:
        team_name (str): The name of the F1 team
    
    Returns:
        str: The hex color code for the team
    """
    if not team_name:
        return "#666666"
    
    color_map = {
        "Red Bull Racing": "#0600EF",
        "Mercedes": "#00D2BE",
        "Ferrari": "#DC0000",
        "McLaren": "#FF8700",
        "Aston Martin": "#006F62",
        "Alpine": "#0090FF",
        "Williams": "#005AFF",
        "RB": "#1E41FF",
        "Racing Bulls": "#1E41FF",
        "VCARB": "#1E41FF",
        "Sauber": "#900000",
        "Haas F1 Team": "#FFFFFF"
    }
    
    return color_map.get(team_name, "#666666")

def get_flag_url(nationality):
    """
    Returns the F1 official website flag URL for a given nationality.
    
    Args:
        nationality (str): The nationality of the driver
    
    Returns:
        str: The URL to the nationality flag image from F1's website
    """
    if not nationality:
        return ""
    
    # Base URL for all F1 website flags
    base_url = "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Flags%2016x9/"
    
    # Map nationalities to their corresponding flag file names
    flags_map = {
        "Dutch": "netherlands-flag.png",
        "British": "great-britain-flag.png",
        "Monegasque": "monaco-flag.png",
        "Spanish": "spain-flag.png",
        "Australian": "australia-flag.png",
        "Mexican": "mexico-flag.png",
        "Finnish": "finland-flag.png",
        "Canadian": "canada-flag.png",
        "Thai": "thailand-flag.png",
        "Japanese": "japan-flag.png",
        "French": "france-flag.png",
        "Danish": "denmark-flag.png",
        "German": "germany-flag.png",
        "American": "united-states-flag.png",
        "Chinese": "china-flag.png",
        "Italian": "italy-flag.png",
        "Brazilian": "brazil-flag.png",
        "New Zealander": "new-zealand-flag.png",
        "Argentinian": "argentina-flag.png",
        "Belgian": "belgium-flag.png",
        "Swiss": "switzerland-flag.png",
        "Russian": "russia-flag.png",
        "Polish": "poland-flag.png",
        "Swedish": "sweden-flag.png",
        "Estonian": "estonia-flag.png",
        "Portuguese": "portugal-flag.png",
        "Indian": "india-flag.png",
        "Austrian": "austria-flag.png",
        "Bahraini": "bahrain-flag.png",
        "Saudi Arabian": "saudi-arabia-flag.png",
        "Emirati": "uae-flag.png",
        "Qatari": "qatar-flag.png",
        "Singaporean": "singapore-flag.png",
        "Hungarian": "hungary-flag.png",
        "Vietnamese": "vietnam-flag.png",
        "Azerbaijani": "azerbaijan-flag.png",
        "South African": "south-africa-flag.png",
        "Malaysian": "malaysia-flag.png",
        "Turkish": "turkey-flag.png",
        "Korean": "south-korea-flag.png",
        "Indonesian": "indonesia-flag.png"
    }
    
    # Get the flag filename from the map or use a default
    flag_filename = flags_map.get(nationality, "")
    
    # If we don't have a mapping for this nationality, return empty string
    if not flag_filename:
        return ""
        
    # Construct and return the full URL
    return base_url + flag_filename

def get_event_image(location):
    base_url = "https://media.formula1.com/image/upload/f_auto,c_limit,w_1440,q_auto/f_auto/q_auto/content/dam/fom-website/2018-redesign-assets/Racehub%20header%20images%2016x9/"
    
    # Map locations to their corresponding image file names
    location_map = {
        "Sakhir": "Bahrain.jpg",
        "Bahrain": "Bahrain.jpg",
        "Jeddah": "Saudi_Arabia.jpg",
        "Saudi Arabia": "Saudi_Arabia.jpg",
        "Suzuka": "Japan.jpg",
        "Japan": "Japan.jpg",
        "Imola": "Italy.jpg",
        "Monaco": "Monaco.jpg",
        "Barcelona": "Spain.jpg",
        "Spain": "Spain.jpg",
        "Montréal": "Canada.jpg", 
        "Montreal": "Canada.jpg",
        "Canada": "Canada.jpg",
        "Spielberg": "Austria.jpg",
        "Austria": "Austria.jpg",
        "Silverstone": "Great_Britain.jpg",
        "Great Britain": "Great_Britain.jpg",
        "Budapest": "Hungary.jpg",
        "Hungary": "Hungary.jpg",
        "Zandvoort": "Netherlands.jpg",
        "Netherlands": "Netherlands.jpg",
        "Monza": "Italy.jpg",
        "Italy": "Italy.jpg",
        "Baku": "Azerbaijan.jpg",
        "Azerbaijan": "Azerbaijan.jpg",
        "Marina Bay": "Singapore.jpg",
        "Singapore": "Singapore.jpg",
        "Mexico City": "Mexico.jpg",
        "Mexico": "Mexico.jpg",
        "Australia": "Australia.jpg",
        "Belgium": "Belgium.jpg",
        "Brazil": "Brazil.jpg",
        "Las Vegas": "Las_Vegas.jpg",
        "Abu Dhabi": "Abu_Dhabi.jpg",
        "Qatar": "Qatar.jpg",
        "United States": "USA.jpg",
        "Miami": "Miami.jpg",
        "China": "China.jpg",
    }
    
    # Return the full image URL if location is in the map
    if location in location_map:
        return base_url + location_map[location]
    
    # Return a default image or None if the location isn't mapped
    return base_url + "Formula1.jpg"  # A default F1 image as fallback

def get_driver_image(driver_name):
    driver_images = {
    # Red Bull Racing
    "Max Verstappen": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/verstappen.jpg.img.1920.medium.jpg",
    "Isack Hadjar": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/hadjar.jpg.img.1920.medium.jpg",
    
    # Ferrari
    "Charles Leclerc": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/leclerc.jpg.img.1920.medium.jpg",
    "Lewis Hamilton": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/hamilton.jpg.img.1920.medium.jpg",
    
    # Mercedes
    "George Russell": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/russell.jpg.img.1920.medium.jpg",
    "Andrea Kimi Antonelli": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/antonelli.jpg.img.1920.medium.jpg",
    
    # McLaren
    "Lando Norris": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/norris.jpg.img.1920.medium.jpg",
    "Oscar Piastri": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/piastri.jpg.img.1920.medium.jpg",
    
    # Aston Martin
    "Fernando Alonso": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/alonso.jpg.img.1920.medium.jpg",
    "Lance Stroll": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/stroll.jpg.img.1920.medium.jpg",
    
    # Alpine
    "Pierre Gasly": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/gasly.jpg.img.1920.medium.jpg",
    "Jack Doohan": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/doohan.jpg.img.1920.medium.jpg",
    
    # RB (Racing Bulls)
    "Yuki Tsunoda": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/tsunoda.jpg.img.1920.medium.jpg",
    "Liam Lawson": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/lawson.jpg.img.1920.medium.jpg",
    
    # Williams
    "Alexander Albon": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/albon.jpg.img.1920.medium.jpg",
    "Carlos Sainz": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/sainz.jpg.img.1920.medium.jpg",
    
    # Haas
    "Esteban Ocon": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/ocon.jpg.img.1920.medium.jpg",
    "Oliver Bearman": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/bearman.jpg.img.1920.medium.jpg",
    
    # Sauber (Audi)
    "Nico Hulkenberg": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/hulkenberg.jpg.img.1920.medium.jpg",
    "Gabriel Bortoleto": "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/bortoleto.jpg.img.1920.medium.jpg"
    }
    # Return the image URL if driver name is in the map
    if driver_name in driver_images:
        return driver_images[driver_name]
    
    # Return a default image or None if the driver isn't mapped
    return "https://media.formula1.com/content/dam/fom-website/drivers/2025Drivers/default.jpg.img.1920.medium.jpg"  # A default F1 image as fallback


# You can also add a convenience function that combines nationality lookup with flag URL
def get_driver_flag(driver_name):
    """
    Returns the flag URL for a given driver name.
    
    Args:
        driver_name (str): The name of the F1 driver
    
    Returns:
        str: The URL to the driver's nationality flag image
    """
    nationality = driver_nationality(driver_name)
    return get_flag_url(nationality)

def get_db_connection():
    """Establish and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None
    

@app.route('/api/standings/drivers', methods=['GET'])
def get_drivers_standings():
    """Retrieve and return driver standings data"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch all driver data
        query = """
            SELECT 
                PlayerId as id,
                Name as name,
                Team as team,
                Image as image,
                Wins as wins,
                Podiums as podiums,
                Points as points,
                ChampionshipWins as championships,
                PlayerNum as number,
                IsActive as isActive,
                Pace as pace,
                Agressiveness as agress,
                Defense as def,
                TireMan as tireman,
                Consistency as consist,
                Qualifying as quali,
                Overall as overall
            FROM Player
            WHERE IsActive != 0
            ORDER BY Points DESC
        """
        
        cursor.execute(query)
        drivers = cursor.fetchall()
        print(drivers)
        print(f"Fetched {len(drivers)} drivers from the database.")
        
        # Add position based on the sorted order and slugify name for URLs
        for i, driver in enumerate(drivers):
            driver['position'] = i + 1
            driver['slug'] = driver['name'].lower().replace(' ', '-')
            driver['image'] = get_driver_image(driver['name'])
            
            # Set default values for required frontend fields
            driver['nationality'] = driver_nationality(driver['name'])
            driver['flag'] = get_driver_flag(driver['name'])
            driver['teamColor'] = get_team_color(driver['team'])

            if driver['pace'] is None:
                driver['pace'] = random.randint(65, 80)
                
            if driver['agress'] is None:
                driver['agress'] = random.randint(65, 80)

            if driver['def'] is None:
                driver['def'] = random.randint(65, 80)

            if driver['tireman'] is None:
                driver['tireman'] = random.randint(65, 80)

            if driver['consist'] is None:
                driver['consist'] = random.randint(65, 80)

            if driver['quali'] is None:
                driver['quali'] = random.randint(65, 80)
                    
            if driver['overall'] is None:
                driver['overall'] = random.randint(65, 80)
                

            
        
        return jsonify(drivers)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/standings/constructors', methods=['GET'])
def get_constructors_standings():
    """Retrieve and return constructor standings data from driver data"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to group drivers by team and sum their points
        query = """
        SELECT 
            Team as name,
            SUM(Points) as points,
            SUM(Wins) as wins
        FROM Player
        GROUP BY Team
        ORDER BY points DESC
        """
        
        cursor.execute(query)
        constructors = cursor.fetchall()
        
        # Add position and ID based on the sorted order
        for i, team in enumerate(constructors):
            team['id'] = i + 1
            team['position'] = i + 1
            
            # Set default values for required fields
            team['color'] = get_team_color(team['name'])
            team['logo'] = ""
            team['country'] = driver_nationality(team['name'])
            team['flag'] = ""
        
        return jsonify(constructors)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/driver/<int:driver_id>', methods=['GET'])
def get_driver_by_id(driver_id):
    """Retrieve and return driver data by ID"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch driver data by ID
        query = """
        SELECT 
            PlayerId as id,
            Name as name,
            Team as team,
            Image as image,
            Wins as wins,
            Podiums as podiums,
            Points as points,
            ChampionshipWins as championships,
            PlayerNum as number,
            IsActive as isActive
        FROM Player
        WHERE PlayerId = %s
        """
        
        cursor.execute(query, (driver_id,))
        driver = cursor.fetchone()
        print(driver)
        if driver:
            driver['slug'] = driver['name'].lower().replace(' ', '-')
            driver['nationality'] = driver_nationality(driver['name'])
            driver['flag'] = get_driver_flag(driver['name'])
            driver['teamColor'] = get_team_color(driver['team'])
            
            return jsonify(driver)
        else:
            return jsonify({"error": "Driver not found"}), 404
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/driver/slug/<string:driver_slug>', methods=['GET'])
def get_driver_by_slug(driver_slug):
    """Retrieve and return driver data by slug"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch all drivers
        query = """
        SELECT 
            PlayerId as id,
            Name as name,
            Team as team,
            Image as image,
            Wins as wins,
            Podiums as podiums,
            Points as points,
            ChampionshipWins as championships,
            PlayerNum as number,
            IsActive as isActive,
            Pace as pace,
            Agressiveness as agress,
            Defense as def,
            TireMan as tireman,
            Consistency as consist,
            Qualifying as quali,
            Overall as overall
        FROM Player
        """
        
        cursor.execute(query)
        drivers = cursor.fetchall()
        print(drivers)
        # Find driver with matching slug
        for driver in drivers:
            # Generate slug from name
            slug = driver['name'].lower().replace(' ', '-')
            if slug == driver_slug:
                driver['slug'] = slug
                driver['nationality'] = driver_nationality(driver['name'])
                driver['flag'] = get_driver_flag(driver['name'])
                driver['teamColor'] = get_team_color(driver['team'])
                driver['image'] = get_driver_image(driver['name'])
                if driver['pace'] is None:
                    driver['pace'] = random.randint(65, 80)
                
                if driver['agress'] is None:
                    driver['agress'] = random.randint(65, 80)

                if driver['def'] is None:
                    driver['def'] = random.randint(65, 80)

                if driver['tireman'] is None:
                    driver['tireman'] = random.randint(65, 80)

                if driver['consist'] is None:
                    driver['consist'] = random.randint(65, 80)

                if driver['quali'] is None:
                    driver['quali'] = random.randint(65, 80)

                if driver['overall'] is None:
                    driver['overall'] = random.randint(65, 80)
                
                return jsonify(driver)
        
        # If we get here, no driver was found
        return jsonify({"error": "Driver not found"}), 404
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/events', methods=['GET'])
def get_events():
    """Retrieve and return all events/races data"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch all events
        query = """
        SELECT 
            EventName as name,
            StartDate as startDate,
            EndDate as endDate,
            Country as country,
            Location as location,
            Winner as winner,
            FastLap as fastLap
        FROM Event
        ORDER BY StartDate ASC
        """
        
        cursor.execute(query)
        events = cursor.fetchall()
        
        # Process data for frontend
        for i, event in enumerate(events):
            event['id'] = i + 1
            event['circuit'] = event['location']
            event['completed'] = False
            print(f"Processing event: {event['location']}")

            
            # Format dates for display
            start_date = event['startDate']
            if isinstance(start_date, datetime):
                event['date'] = start_date.strftime('%B %d, %Y')
                event['time'] = start_date.strftime('%H:%M GMT')
            
            # Determine if the race is completed
            now = datetime.now()
            event['completed'] = event['endDate'] < now if isinstance(event['endDate'], datetime) else False
            event['flag'] = get_flag_url(event['country'])

            # Add fastest lap holder name if available
            if event['fastLap'] and event['fastLap'] > 0:
                # miliseconds to m:s:ms
                event['fastLap'] = event['fastLap'] / 1000
            else:
                event['fastestLap'] = "N/A"

            
                
        return jsonify(events)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/event/<int:event_id>', methods=['GET'])
def get_event_by_id(event_id):
    """Retrieve and return event data by ID"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch all events first
        query = """
        SELECT 
            EventName as name,
            StartDate as startDate,
            EndDate as endDate,
            Country as country,
            Location as location,
            Winner as winner,
            FastLap as fastLap
        FROM Event
        ORDER BY StartDate ASC
        """
        
        cursor.execute(query)
        all_events = cursor.fetchall()
        
        # Find the event with the matching ID (since we're generating IDs)
        if 0 <= event_id - 1 < len(all_events):
            event = all_events[event_id - 1]
            event['id'] = event_id
            event['circuit'] = event['location']
            event['image'] = get_event_image(event['location'])
            
            # Format dates
            start_date = event['startDate']
            if isinstance(start_date, datetime):
                event['date'] = start_date.strftime('%B %d, %Y')
                event['time'] = start_date.strftime('%H:%M GMT')
            
            # Add country flag
            event['flag'] = get_flag_url(event['country'])
            
            # Determine if the race is completed
            now = datetime.now()
            event['completed'] = event['endDate'] < now if isinstance(event['endDate'], datetime) else False
            
            # Get fastest lap holder name if available
            if event['fastLap'] and event['fastLap'] > 0:
                fastlap_query = "SELECT Name FROM Player WHERE PlayerId = %s"
                cursor.execute(fastlap_query, (event['fastLap'],))
                fastlap_result = cursor.fetchone()
                event['fastestLap'] = fastlap_result['Name'] if fastlap_result else "Unknown"
            else:
                event['fastestLap'] = "N/A"
                
            return jsonify(event)
        else:
            return jsonify({"error": "Event not found"}), 404
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/future-events', methods=['GET'])
def get_future_events():
    """Retrieve and return all future events data"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch all future events
        query = """
        SELECT 
            EventName as name,
            Date as startDate,
            Country as country,
            Location as location
        FROM FutureEvent
        ORDER BY Date ASC
        """
        
        cursor.execute(query)
        events = cursor.fetchall()
        
        # Process data for frontend
        for i, event in enumerate(events):
            event['id'] = i + 1
            event['circuit'] = event['location']
            
            # Format dates for display
            start_date = event['startDate']
            if isinstance(start_date, datetime):
                event['date'] = start_date.strftime('%B %d, %Y')
                event['time'] = start_date.strftime('%H:%M GMT')
            
            # Add future event flag
            event['isFutureEvent'] = True
            event['completed'] = False
            event['flag'] = get_flag_url(event['country'])
                
        return jsonify(events)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/all-events', methods=['GET'])
def get_all_events():
    """Retrieve and return both past/current events and future events"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch regular events
        events_query = """
        SELECT 
            EventName as name,
            StartDate as startDate,
            EndDate as endDate,
            Country as country,
            Location as location,
            Winner as winner,
            FastLap as fastLap,
            FALSE as isFutureEvent
        FROM Event
        ORDER BY StartDate ASC
        """
        
        # Query to fetch future events
        future_query = """
        SELECT 
            EventName as name,
            Date as startDate,
            NULL as endDate,
            Country as country,
            Location as location,
            NULL as winner,
            NULL as fastLap,
            TRUE as isFutureEvent
        FROM FutureEvent
        ORDER BY Date ASC
        """
        
        cursor.execute(events_query)
        regular_events = cursor.fetchall()
        
        cursor.execute(future_query)
        future_events = cursor.fetchall()
        
        # Combine and sort all events
        all_events = regular_events + future_events
        all_events.sort(key=lambda x: x['startDate'])
        
        # Process data for frontend
        for i, event in enumerate(all_events):
            event['id'] = i + 1
            event['circuit'] = event['location']
            event['image'] = get_event_image(event['location'])
            print(f"Processing event: {event['location']}")
            
            # Format dates for display
            start_date = event['startDate']
            if isinstance(start_date, datetime):
                event['date'] = start_date.strftime('%B %d, %Y')
                event['time'] = start_date.strftime('%H:%M GMT')
            
            # Determine if the race is completed
            now = datetime.now()
            if not event['isFutureEvent']:
                event['completed'] = event['endDate'] < now if isinstance(event['endDate'], datetime) else False
            else:
                event['completed'] = False
                
            event['flag'] = get_flag_url(event['country'])

            # Add fastest lap holder name if available
            if not event['isFutureEvent'] and event['fastLap'] and event['fastLap'] > 0:
                fastlap_query = "SELECT Name FROM Player WHERE PlayerId = %s"
                cursor.execute(fastlap_query, (event['fastLap'],))
                fastlap_result = cursor.fetchone()
                event['fastestLap'] = fastlap_result['Name'] if fastlap_result else "Unknown"
            else:
                event['fastestLap'] = "N/A"
                
        return jsonify(all_events)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/team/<string:team_name>', methods=['GET'])
def get_team_details(team_name):
    """Retrieve and return team details and its drivers"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch drivers from the team
        query = """
        SELECT 
            PlayerId as id,
            Name as name,
            Team as team,
            Image as image,
            Wins as wins,
            Podiums as podiums,
            Points as points,
            ChampionshipWins as championships,
            PlayerNum as number,
            IsActive as isActive
        FROM Player
        WHERE Team = %s
        ORDER BY Points DESC
        """
        
        cursor.execute(query, (team_name,))
        drivers = cursor.fetchall()
        
        if not drivers:
            return jsonify({"error": "Team not found"}), 404
        
        # Process driver data
        for driver in drivers:
            driver['nationality'] = driver_nationality(driver['name'])
            driver['flag'] = get_driver_flag(driver['name'])
            driver['slug'] = driver['name'].lower().replace(' ', '-')
        
        # Query to get team points
        points_query = """
        SELECT SUM(Points) as total_points, SUM(Wins) as total_wins
        FROM Player
        WHERE Team = %s
        """
        
        cursor.execute(points_query, (team_name,))
        team_stats = cursor.fetchone()
        
        # Construct team response
        team_response = {
            "name": team_name,
            "color": get_team_color(team_name),
            "points": team_stats['total_points'] if team_stats else 0,
            "wins": team_stats['total_wins'] if team_stats else 0,
            "drivers": drivers
        }
        
        return jsonify(team_response)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/next-race', methods=['GET'])
def get_next_race():
    """Return the next upcoming race"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get current date
        now = datetime.now()
        
        # Query to fetch the next upcoming race
        query = """
        SELECT 
            EventName as name,
            StartDate as startDate,
            EndDate as endDate,
            Country as country,
            Location as location, 
            Winner as winner,
            FastLap as fastLap
        FROM Event 
        WHERE StartDate > %s
        ORDER BY StartDate ASC
        LIMIT 1
        """
        
        cursor.execute(query, (now,))
        next_race = cursor.fetchone()
        
        if not next_race:
            return jsonify({"error": "No upcoming races found"}), 404
        
        # Add additional formatted information
        next_race['id'] = 1  # Assign an ID for consistency
        next_race['circuit'] = next_race['location']
        next_race['completed'] = False
        
        # Format dates for display
        start_date = next_race['startDate']
        if isinstance(start_date, datetime):
            next_race['date'] = start_date.strftime('%B %d, %Y')
            next_race['time'] = start_date.strftime('%H:%M GMT')
            # Add ISO format for JavaScript Date parsing
            next_race['dateTime'] = start_date.timestamp() * 1000  # Convert to milliseconds for JS
        
        # Add country flag
        next_race['flag'] = get_flag_url(next_race['country'])
        
        # Get fastest lap holder name if available and applicable
        if next_race['fastLap'] and next_race['fastLap'] > 0:
            fastlap_query = "SELECT Name FROM Player WHERE PlayerId = %s"
            cursor.execute(fastlap_query, (next_race['fastLap'],))
            fastlap_result = cursor.fetchone()
            next_race['fastestLap'] = fastlap_result['Name'] if fastlap_result else "Unknown"
        else:
            next_race['fastestLap'] = "TBD"
        
        return jsonify(next_race)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/next-races', methods=['GET'])
def get_next_races():
    """Return upcoming races including both scheduled and future events"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get current date
        now = datetime.now()
        
        # Query to fetch upcoming regular events
        events_query = """
        SELECT 
            EventName as name,
            StartDate as startDate,
            EndDate as endDate,
            Country as country,
            Location as location, 
            Winner as winner,
            FastLap as fastLap,
            FALSE as isFutureEvent
        FROM Event 
        WHERE StartDate > %s
        ORDER BY StartDate ASC
        """
        
        # Query to fetch future events
        future_query = """
        SELECT 
            EventName as name,
            Date as startDate,
            NULL as endDate,
            Country as country,
            Location as location,
            NULL as winner,
            NULL as fastLap,
            TRUE as isFutureEvent
        FROM FutureEvent
        WHERE Date > %s
        ORDER BY Date ASC
        """
        
        cursor.execute(events_query, (now,))
        upcoming_events = cursor.fetchall()
        
        cursor.execute(future_query, (now,))
        future_events = cursor.fetchall()
        
        # Combine and sort all upcoming events
        next_races = upcoming_events + future_events
        next_races.sort(key=lambda x: x['startDate'])
        
        # Limit to a reasonable number for display
        limit = int(request.args.get('limit', 5))
        next_races = next_races[:limit]
        
        # Format event data
        for i, race in enumerate(next_races):
            race['id'] = i + 1
            race['circuit'] = race['location']
            race['completed'] = False
            
            # Format dates for display
            start_date = race['startDate']
            if isinstance(start_date, datetime):
                race['date'] = start_date.strftime('%B %d, %Y')
                race['time'] = start_date.strftime('%H:%M GMT')
                race['dateTime'] = start_date.timestamp() * 1000  # Convert to milliseconds for JS
            
            # Add country flag
            race['flag'] = get_flag_url(race['country'])
            
            # Set fastest lap information
            race['fastestLap'] = "TBD"
        
        return jsonify(next_races)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/search', methods=['GET'])
def search():
    """Search for drivers, teams, or events"""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify({"error": "Search query too short"}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Search for drivers
        driver_query = """
        SELECT 
            PlayerId as id,
            Name as name,
            'driver' as type
        FROM Player
        WHERE Name LIKE %s
        LIMIT 5
        """
        
        # Search for events
        event_query = """
        SELECT 
            EventName as name,
            'event' as type
        FROM Event
        WHERE EventName LIKE %s OR Country LIKE %s OR Location LIKE %s
        LIMIT 5
        """
        
        # Search for teams
        team_query = """
        SELECT DISTINCT
            Team as name,
            'team' as type
        FROM Player
        WHERE Team LIKE %s
        LIMIT 5
        """
        
        # Execute queries with wildcard search
        search_param = f'%{query}%'
        cursor.execute(driver_query, (search_param,))
        drivers = cursor.fetchall()
        
        cursor.execute(event_query, (search_param, search_param, search_param))
        events = cursor.fetchall()
        
        cursor.execute(team_query, (search_param,))
        teams = cursor.fetchall()
        
        # Combine results
        results = drivers + events + teams
        
        # Add additional metadata for UI
        for item in results:
            if item['type'] == 'driver':
                item['url'] = f"/driver/{item['name'].lower().replace(' ', '-')}"
            elif item['type'] == 'event':
                item['url'] = f"/schedule"
            elif item['type'] == 'team':
                item['url'] = f"/team/{item['name'].replace(' ', '-').lower()}"
        
        return jsonify(results)
    
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# Get API configurations from environment variables
LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "unsloth/Meta-Llama-3.1-8B-Instruct")

# Add this function to chat_service.py
def get_fallback_response(user_message):
    """Provides a fallback response when LLM is unavailable"""
    user_message = user_message.lower()
    
    if any(word in user_message for word in ['win', 'champion']):
        return "Based on current form, Max Verstappen remains the favorite for race wins, but Charles Leclerc and Lando Norris have shown impressive pace recently. The championship battle is far from over, with Red Bull facing stronger competition from Ferrari and McLaren than in previous seasons."
    elif any(word in user_message for word in ['strategy', 'tactics']):
        return "Ferrari has significantly improved their race strategy execution this season. They've addressed previous weaknesses in tire management and timing of pit stops. However, Red Bull still maintains the edge in adapting to changing conditions mid-race, particularly with their outstanding pit crew performance."
    elif any(word in user_message for word in ['verstappen', 'max']):
        return "Max Verstappen's driving style combines exceptional car control with relentless aggression. His key strengths include incredible braking precision, mid-corner adjustments that few other drivers can execute, and exceptional tire management despite his aggressive style."
    elif any(word in user_message for word in ['red bull', 'redbull']):
        return "Red Bull's current dominance stems from their exceptional aerodynamic efficiency. Adrian Newey's design philosophy has created a car with remarkable balance through high and low-speed corners while maintaining excellent straight-line speed."
    else:
        return "Formula 1 is a complex sport with many technical and strategic elements. Teams continuously develop their cars throughout the season while drivers need to balance raw speed with consistency. The regulations create a framework for innovation while ensuring safety and fair competition."

def get_llm_client():
    """Initialize and return the LLM client"""
    return OpenAI(
        model_name=LLM_MODEL,
        temperature=0.6,
        openai_api_key=LLM_API_KEY,
        openai_api_base=LLM_API_URL
    )

@app.route('/api/chat', methods=['POST'])
def chat_response():
    """Handle chat request and return AI response"""
    print("Received chat request")
    if not request.json or 'message' not in request.json:
        return jsonify({"error": "Invalid request, 'message' field required"}), 400
    
    user_message = request.json['message']
    
    try:
        # Format the prompt with F1 expert context
        prompt = f"""You are an F1 Expert Analyst assistant with deep knowledge about Formula 1 racing. 
        You provide professional, in-depth analysis on races, drivers, teams, and technical aspects of Formula 1.
        
        User's question: {user_message}
        
        Provide a concise and insightful answer using the data provided and your knowledge of F1. 
        BE VERY BRIEF - LIMIT YOUR RESPONSE TO APPROXIMATELY 100 WORDS.
        Be precise and informative.
        Be friendly and engaging.
        """
        
        # Get the LLM client and generate response
        try:
            llm = get_llm_client()
            response = llm.invoke(prompt)
        except Exception as llm_error:
            print(f"LLM error: {llm_error}, using fallback")
            response = get_fallback_response(user_message)
        
        return jsonify({
            "message": response,
            "user": "F1 Analyst"
        })
        
    except Exception as e:
        print(f"Error generating response: {e}")
        fallback_response = get_fallback_response(user_message)
        return jsonify({
            "message": fallback_response,
            "user": "F1 Analyst"
        }), 200


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=True)