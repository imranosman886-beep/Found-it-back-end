# FoundIt Backend

## About the Project

FoundIt is a web-based lost and found platform that helps users report lost items, report found items, and reconnect people with their belongings.

This repository contains the Flask REST API that handles authentication, database operations, item management, claims, notifications, and image uploads.

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Flask-Migrate
- Flask-Bcrypt
- Flask-CORS
- Cloudinary
- SendGrid
- Pytest

## Features

- User registration and login
- Session-based authentication
- Secure password hashing
- User account management
- Lost item reporting and management
- Found item reporting and management
- Item categories
- Claim submission and management
- Notifications
- Admin management
- Image uploads using Cloudinary
- Email sending using SendGrid
- Pagination for listing endpoints
- User ownership and access control
- Input validation and error handling

## Project Structure

```text
Found-it-back-end/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
│
├── server/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── categories.py
│   │   ├── lost_items.py
│   │   ├── found_items.py
│   │   ├── claims.py
│   │   ├── notifications.py
│   │   └── uploads.py
│   │
│   ├── services/
│   └── utils/
│
├── migrations/
├── tests/
└── docs/
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/imranosman886-beep/Found-it-back-end.git
```

### 2. Enter the Project Folder

```bash
cd Found-it-back-end
```

### 3. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 4. Activate the Virtual Environment

For Linux or WSL:

```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root directory.

Add the following configuration, replacing the example values with your own credentials:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_postgresql_database_url

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender_email
```

Keep your credentials private. Never commit your `.env` file to GitHub.

## Database Setup

Make sure PostgreSQL is installed and running and your database exists.

Run the database migrations:

```bash
flask db upgrade
```

## Running the Backend

Start the Flask application:

```bash
python app.py
```

The backend runs at:

```text
http://localhost:5555
```

## API Features

The API is organized into different route modules:

| Module | Responsibility |
|---|---|
| Authentication | Registration, login, session checking and logout |
| Categories | Managing item categories |
| Lost Items | Reporting and managing lost items |
| Found Items | Reporting and managing found items |
| Claims | Managing claims for found items |
| Notifications | Managing user notifications |
| Admin | Administrative operations |
| Uploads | Handling image uploads |

## Authentication

FoundIt uses session-based authentication.

Users must log in before accessing protected resources. The backend uses secure password hashing and checks resource ownership to prevent users from accessing other users' private data.

The React frontend must include credentials when making requests to the backend so that session cookies are sent.

## Running Tests

Make sure your virtual environment is activated.

Run all tests:

```bash
python -m pytest -v
```

## Team Collaboration

The project is developed using Git and GitHub.

Team members work on separate branches and submit pull requests for code review and integration.

## Contributors

- Imran – Backend development and integration
- Faith – Authentication and admin management
- Beatrice – Categories and found items
- Abdimajid – Lost items
- Priscillah – Claims and notifications

## Repository

[FoundIt Backend on GitHub](https://github.com/imranosman886-beep/Found-it-back-end)
