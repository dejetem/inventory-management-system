# Getting Started

## Inventory Management System
This project is a RESTful API for managing products, suppliers, and inventory levels. It is built using Django REST Framework (DRF) and includes features like JWT authentication, CSV file upload, background task processing, and Dockerization.



In the project directory, you can run:
## Setup to run the application

## Clone the Repository
#### `git clone https://github.com/yourusername/inventory-management-system.git`
#### `cd inventory-management-system`

#### `create a .env and copy the data from the .env.example file in the .env and input the required data`
#### `Install Docker on your system.`
#### `docker compose build`
#### `docker compose up`
#### `docker exec -it <container_name_or_id> python manage.py migrate` 

## Available Scripts

To makemigrations
#### `docker ps`
#### `docker exec -it <container_name_or_id> python manage.py makemigrations` 

To run migration
#### `docker ps`
#### `docker exec -it <container_name_or_id> python manage.py migrate` 

To run test
#### `docker ps`
#### `docker exec -it <container_name_or_id> python manage.py test` 

To run test coverage
#### `docker ps`
#### `docker exec -it <container_name_or_id> coverage run manage.py test` 
#### `docker exec -it 3ef3c4be733f coverage report` 
#### `docker exec -it 3ef3c4be733f coverage html` 
Open the index.html file in your web browser to view the detailed coverage report. You can do this by running:
On Linux/Mac
```bash
   open htmlcov/index.html
```
On Windows
```bash
   start htmlcov/index.html
```
Runs the app in the development mode.\
BaseUrl 
#### `http://127.0.0.1:8000`

## API documentation
```bash
   http://localhost:8000/api/docs/
```
Test the CSV Upload
```bash
curl -X POST -H "Authorization: Bearer <your access token>" -F "file=@product-data.csv" http://localhost:8000/api/upload-csv/
```




Design Choices, Dockerization, and Deployment
Below is a brief write-up explaining the design choices, Dockerization, and deployment of the Inventory Management System project.

1. Design Choices
1.1. Django REST Framework (DRF)
Why DRF?

DRF is a powerful and flexible toolkit for building Web APIs in Django.

It provides built-in support for authentication, serialization, and pagination, which are essential for this project.

DRF’s browsable API makes it easy to test and document endpoints.

1.2. JWT Authentication
Why JWT?

JSON Web Tokens (JWT) are stateless and scalable, making them ideal for RESTful APIs.

JWTs are secure and can be easily integrated with DRF using the djangorestframework-simplejwt library.

JWTs allow for easy user authentication and authorization.

1.3. Celery for Background Tasks
Why Celery?

Celery is a distributed task queue that allows long-running tasks (e.g., CSV processing, report generation) to be handled asynchronously.

It ensures that the API remains responsive while processing large files or generating reports.

Celery integrates seamlessly with Django and supports Redis as a message broker.

1.4. MySQL Database
Why MySQL?

MySQL is a robust, scalable, and widely-used relational database.

It supports complex queries and transactions, which are essential for managing inventory data.

Django’s ORM makes it easy to interact with MySQL without writing raw SQL queries.

1.5. MVC Design Pattern
Why MVC?

The Model-View-Controller (MVC) pattern separates concerns, making the codebase modular and maintainable.

Models handle data logic, views handle business logic, and serializers handle data representation.

This separation ensures that the code is clean, scalable, and easy to debug.

2. Dockerization
2.1. Why Docker?
Docker allows the application to be packaged into containers, ensuring consistency across development, testing, and production environments.

It simplifies dependency management and eliminates the "it works on my machine" problem.

Docker Compose makes it easy to manage multi-container setups (e.g., Django app + MySQL database).

2.2. Dockerfile
The Dockerfile defines the environment for the Django application:

Base Image: python:3.12-slim is a lightweight Python image.

Dependencies: Installs all Python dependencies from requirements.txt.

Application Code: Copies the entire project into the container.

Command: Runs the Django development server.

2.3. docker-compose.yml
The docker-compose.yml file defines the multi-container setup:

Web Service: Builds the Django app and maps port 8000.

DB Service: Uses the official MySQL 8.0 image and sets up the database.

Redis: Redis as a message broker

Celery: Celery is a distributed task queue that allows long-running tasks


2.4. Running the Application
To start the application:

```bash
   docker-compose up --build
```
This command builds the Docker images and starts the containers.


3. Deployment
3.1. Why Render?
Render is a modern cloud platform that supports Dockerized applications.

It provides automatic scaling, SSL, and continuous deployment from GitHub.

Render’s free tier is sufficient for small projects like this one.


4. Testing and Code Coverage
4.1. Why Django’s Built-in Testing Framework?
Django’s testing framework is simple, powerful, and integrates seamlessly with the Django ecosystem.

It supports unit tests, integration tests, and API tests.

4.2. Code Coverage
The coverage tool is used to measure code coverage.

Tests are written to ensure 91% coverage of all views, models, and serializers.

Coverage reports are generated in both terminal and HTML formats.


5. Documentation
5.1. API Documentation
DRF’s built-in browsable API is used for documentation.

Endpoints are documented using drf_yasg.


6. Conclusion
This project demonstrates best practices for building a RESTful API using Django REST Framework. Key features include:

JWT Authentication for secure user access.

Celery for background task processing.

Docker for containerization and deployment.

MySQL for reliable data storage.

100% Test Coverage to ensure code quality.

The project is modular, scalable, and ready for production deployment. Let me know if you need further assistance!
