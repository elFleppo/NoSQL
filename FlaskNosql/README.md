# Music Database Application

A Flask-based web application for managing a classical music database using MongoDB. The application allows users to add, search, and view information about composers, pieces, orchestras, conductors, and reviews.

## Prerequisites

- Python 3.x
- MongoDB
- Docker and Docker Compose (for containerized deployment)

## Local Development Setup

1. Clone the repository
2. Install required Python packages:
   ```bash
   pip install flask flask-cors pymongo
   ```
3. Start MongoDB locally
4. Update the MongoDB connection string in `app.py` if needed
5. Run the Flask application:
   ```bash
   python app.py
   ```
6. Access the application at `http://localhost:5000`

## Docker Deployment

1. Ensure Docker and Docker Compose are installed
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application at `http://localhost:5000`

## Available Routes

### Web Pages
- `/home` - Landing page with application overview
- `/testing` - Form page for adding new data
- `/searchpage` - Search interface for querying the database

### API Endpoints
- `/search` (GET)
  - Parameters:
    - `q`: Search query string
    - `entity_type`: Type of entity to search (Composer, Piece, Orchestra, Conductor, Review, or 'all')
  - Returns: JSON object containing search results grouped by entity type

- `/get_entities/<entity_type>` (GET)
  - Parameters:
    - `entity_type`: Type of entity to retrieve (Composer, Piece, Orchestra, Conductor, Review)
  - Returns: JSON array of entities of the specified type

- `/add_document` (POST)
  - Parameters:
    - `entity_type`: Type of entity being added (via query parameter)
    - JSON body: Document data to be added
  - Returns: JSON object with success message and inserted document ID

## Entity Types and Fields

### Composer
- name
- nationality

### Piece
- piece_name
- composer_id
- orchestra_id
- era

### Orchestra
- orchestra_name
- conductor_id

### Conductor
- firstname
- lastname
- age

### Review
- text_content
- score
- date

## Database Structure

The application uses MongoDB with the following collections:
- composers
- pieces
- orchestras
- conductors
- reviews 