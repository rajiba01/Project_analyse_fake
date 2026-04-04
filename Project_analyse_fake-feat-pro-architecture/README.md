# Analyse IA Project

## Overview
This project, named "Analyse IA", is a Django application designed for collaborative analysis and insights. It serves as a foundation for building AI-driven features and functionalities.

## Project Structure
The project is organized as follows:

```
analyse-ia
├── analyse_ia
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.x installed on your machine.
- pip (Python package installer) should be available.

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd analyse-ia
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

### Usage
Once the server is running, you can access the application at `http://127.0.0.1:8000/`.

### Collaboration
To collaborate effectively:
- Ensure you are using the same Python version.
- Regularly pull changes from the main branch.
- Use feature branches for new developments and create pull requests for merging.

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgments
Thanks to all contributors for their efforts in making this project a success.