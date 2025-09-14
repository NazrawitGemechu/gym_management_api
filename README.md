# Gym Management API

This project provides a RESTful API for managing a gym, including users, membership passes, and gym visits. It's built using Django REST Framework, and designed to be run with Docker.

## Functionalities

### User Management
- **User Roles**: Supports three distinct roles: `client`, `coach`, and `administrator`.
- **Authentication**: Users can log in to obtain an access token.
- **Password Management**: Authenticated users can change their own passwords.
- **Coach Assignment**: Administrators can assign coaches to clients.
- **Client-Coach Relationships**: Coaches can view their assigned clients, and administrators can view clients with their assigned coaches.

### Membership Management
- **Membership Types**: Supports monthly and annual membership passes.
- **Membership Assignment**: Administrators can assign membership passes to clients.
- **Membership Revocation**: Administrators can revoke active membership passes.
- **Membership Status**: Clients can view their membership passes.

### Gym Visit Tracking
- **Check-in**: Clients with active and valid membership passes can check into the gym.
- **Visit History**: Clients can view their gym visit history.
- **Coach/Admin View**: Coaches can view visit history for their clients, and administrators can view all gym visits.

### Dashboard Views
- **Client Dashboard**: Shows active membership, expiring memberships soon, and recent gym visits.
- **Coach Dashboard**: Displays the number of clients and a list of assigned clients.
- **Administrator Dashboard**: Provides an overview of total users, clients, coaches, active/expiring memberships, visits in the last 30 days, and new members in the last week.

## Tests

*   Tests are located in `gym/tests.py` and use `pytest`.
*   Covers administrator actions (assigning coaches, managing memberships).
*   Covers client actions (gym check-in).

## Installation and Running Instructions (Docker)

### Setup

1.  Navigate to the project root directory: `cd gym_api`
2.  Create a `.env` file with PostgreSQL environment variables:
    ```
    POSTGRES_DB=gym_db
    POSTGRES_USER=gym_user
    POSTGRES_PASSWORD=gym_password
    ```
3.  Build and run Docker containers: `docker-compose up --build -d`
4.  Run database migrations:
   ```
   docker-compose run web python manage.py makemigrations
   docker-compose run web python manage.py migrate
   ```
An administrator user will be automatically created upon running migrations if one does not already exist. The default credentials are admin@gmail.com with password Admin123*

### Accessing the API

*   The API will be accessible at `http://localhost:8000/`.

### Running Tests

*   Execute tests within the Docker container: `docker-compose run web pytest`


