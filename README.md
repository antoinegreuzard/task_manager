# Your Django Project Title

A brief description of your Django project.

## Setting Up Your Development Environment

To set up your development environment, follow these steps:

### Prerequisites

- Python 3.10 minimum
- pip
- venv (optional but recommended)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/antoinegreuzard/task_manager.git
cd task_manager
```

2. Create a virtual environment (optional):

```bash
python -m venv venv
```

- On Windows, activate the virtual environment:

```bash
.\venv\Scripts\activate
```

- On MacOS/Linux:

```bash
source venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

- Copy the `.env.example` file to `.env` and adjust the configurations according to your needs.

```bash
cp .env.example .env
```

### Running the Project

1. Perform migrations:

```bash
python manage.py migrate
```

2. Start the development server:

```bash
python manage.py runserver
```

The server should be running, and you can access your project at `http://127.0.0.1:8000/`.

## Features

- Task filtering by status, priority, or deadline.
- Task status tracking (e.g., New, In Progress, Completed).
- Pagination for task lists.
- Task search functionality.
- User authentication and permissions management.
- Unit testing for models, forms, and views.
- REST API for integration with other services or frontend applications.
- Enhanced UI with CSS frameworks like Bootstrap or Tailwind CSS.
- Notifications for approaching deadlines or task status updates.
- Detailed documentation for the API and the codebase.

## Testing

To run tests:

```bash
python manage.py test
```
