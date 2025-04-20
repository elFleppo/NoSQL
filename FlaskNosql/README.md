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

## Importing Data into MongoDB Docker Container

To import the sample data into your MongoDB Docker container:

1. First, ensure your MongoDB container is running:
   ```bash
   docker ps
   ```

2. Copy the database dump to your container:
   ```bash
   docker cp ./dump <container_name>:/dump
   ```

3. Restore the dump inside the container:
   ```bash
   docker exec -it <container_name> mongorestore /dump
   ```

## API Endpoints

### Authentication

1. Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"
```

2. Register
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=new_user&password=new_password&is_admin=false"
```

3. Logout
```bash
curl -X GET http://localhost:5000/logout
```

4. Check Login Status
```bash
curl -X GET http://localhost:5000/check_login
```

5. Check Admin Status
```bash
curl -X GET http://localhost:5000/check_admin
```

### Data Operations

1. Search
```bash
curl -X GET "http://localhost:5000/search?q=search_term&entity_type=all"
```
Parameters:
- `q`: Search query string
- `entity_type`: Type of entity to search (Composer, Piece, Orchestra, Conductor, Review, or 'all')
Returns: JSON object containing search results grouped by entity type

2. Get Entities by Type
```bash
curl -X GET "http://localhost:5000/get_entities/Composer"
```
Parameters:
- `entity_type`: Type of entity to retrieve (Composer, Piece, Orchestra, Conductor, Review)
Returns: JSON array of entities of the specified type

3. Add Document
```bash
curl -X POST "http://localhost:5000/add_document?entity_type=Composer" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "nationality": "British"}'
```
Parameters:
- `entity_type`: Type of entity being added (via query parameter)
- JSON body: Document data to be added
Returns: JSON object with success message and inserted document ID

4. Edit Document
```bash
curl -X POST "http://localhost:5000/edit_document/Composer/document_id" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "nationality": "Updated Nationality"}'
```

## Database Structure

The application uses MongoDB with the following collections and their fields:

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
- user_id
- piece_id

## Security Notes

- All API endpoints except `/login`, `/register`, and `/check_login` require authentication
- Only admin users can add or edit non-review entities
- Regular users can only add reviews
- Session cookies are set to expire after 1 day
- CSRF protection is enabled through SameSite cookie policy

## Available Routes

### Web Pages
- `/home` - Landing page with application overview
- `/add_document` - Form page for adding new data
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