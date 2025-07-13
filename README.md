# FastAPI Project

## Overview
This FastAPI project is designed to provide a robust and scalable web application framework. It includes features such as user authentication, role-based access control, real-time updates via WebSocket, and a caching layer using Redis.

## Project Structure
The project is organized into several directories and files, each serving a specific purpose:

- **alembic/**: Contains database migration scripts.
- **app/**: The main application directory.
  - **api/**: Contains API route handlers.
    - **v1/**: Version 1 of the API.
      - **routers/**: API routers for different features.
      - **dependencies.py**: Common dependencies for the API.
  - **auth/**: Handles authentication and security.
  - **cache/**: Implements caching functionality.
  - **core/**: Core configurations and settings.
  - **models/**: ORM models for the application.
  - **schemas/**: Pydantic schemas for data validation.
  - **repositories/**: Data access layer for CRUD operations.
  - **services/**: Business logic layer.
  - **routers/**: Modular routes for different features.
  - **utils/**: Utility functions for various tasks.
  - **websockets/**: Logic for real-time updates via WebSocket.
- **.env**: Environment variables for configuration.
- **.gitignore**: Specifies files to ignore in Git.
- **main.py**: Entry point of the FastAPI application.
- **requirements.txt**: Lists project dependencies.
- **alembic.ini**: Configuration for Alembic.

## Features
- **User Management**: Create, update, and retrieve user information.
- **Authentication**: Secure login and token generation using JWT.
- **Role-Based Access Control**: Manage user roles and permissions.
- **Real-Time Updates**: WebSocket support for live updates.
- **Caching**: Redis caching for improved performance.

## Installation

### Prerequisites
- Python 3.9 or higher
- MySQL database
- Redis (optional, for caching)
- Docker (optional, for containerized deployment)

### Steps
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd fastapi_project
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
if face some issue write this command
-- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Configure the `.env` file:
   - Create a `.env` file in the root directory.
   - Add the following environment variables:
     ```
     DATABASE_URL=mysql+pymysql://<username>:<password>@<host>/<database_name>
     SECRET_KEY=<your_secret_key>
     ```

7. Run database migrations:
- **Initialize Alembic** (if not already done):
  ```
  alembic init alembic
  ```
- **Generate a migration**:
  ```
  alembic revision --autogenerate -m "Initial migration"
  ```
- **Apply the migration**:
  ```
  alembic upgrade head
  ```
   **Apply the migration for all single commmand**:
  ```
  python migrate.py
  ```

## Usage
To run the application, execute the following command:
```
uvicorn main:app --reload
if browser blank
uvicorn main:app --reload --port 8001
```
git hub code space : python -m uvicorn main:app --host 0.0.0.0 --port 8000
The application will be available at `http://127.0.0.1:8000`.

## Deployment with Docker
1. Build the Docker image:
   ```
   docker build -t fastapi_project .
   ```
2. Run the Docker container:
   ```
   docker run -d -p 8000:8000 --env-file .env fastapi_project
   ```

## Troubleshooting

### Common Errors and Fixes

1. **Database Connection Error**
   - **Error**: `sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError)`
   - **Fix**: Ensure the `DATABASE_URL` in the `.env` file is correct and the MySQL server is running.

2. **Missing Dependencies**
   - **Error**: `ModuleNotFoundError: No module named '<module_name>'`
   - **Fix**: Run `pip install -r requirements.txt` to install missing dependencies.

3. **Migration Issues**
   - **Error**: `alembic.util.exc.CommandError: Can't locate revision identified by '<revision_id>'`
   - **Fix**: Ensure the database is up-to-date by running `alembic upgrade head`.

4. **CORS Issues**
   - **Error**: `Access to fetch at '<url>' from origin '<origin>' has been blocked by CORS policy.`
   - **Fix**: Update the CORS middleware in `core/middleware.py` to allow the required origins.

5. **Redis Connection Error**
   - **Error**: `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379.`
   - **Fix**: Ensure Redis is installed and running. Update the Redis configuration in the `.env` file if necessary.

6. **Docker Build Issues**
   - **Error**: `Error response from daemon: failed to build: ...`
   - **Fix**: Ensure the `Dockerfile` is correctly configured and all required files are in the project directory.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
