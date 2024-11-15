# Clients API

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Download the project zip file.
2. Unzip the file and navigate to the project directory.
3. Create a virtual environment and activate it:
```python
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```
4. Install the required dependencies:
```
pip install -r requirements.txt
```
5. Create .env using .env.example and fill it with your credentials

### Running the API

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```
2. The API will be available at `http://localhost:8000/docs`.

## Usage

The Clients API provides the following endpoints:

- `POST /clients`: Create a new client.
- `GET /clients`: Retrieve all clients.
- `GET /clients/{client_id}`: Retrieve a specific client by ID.
- `PUT /clients/{client_id}`: Update an existing client.
- `DELETE /clients/{client_id}`: Delete a client.

You can explore and test the API using the interactive Swagger UI documentation available at `http://localhost:8000/docs`.

## Testing

To run the test suite, use the following command:
```bash
pytest tests/
```
This will execute the test cases defined in the `tests/` directory.
