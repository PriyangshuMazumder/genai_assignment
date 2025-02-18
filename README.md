# FastAPI Server Setup for Resume Scoring using LLMs

This guide provides step-by-step instructions to set up and run a FastAPI server in a virtual environment. 
Tested on Postman
Video Link : 

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package manager)

## Steps to Set Up and Run the Server

1. **Create a Virtual Environment**
   ```sh
   python3 -m venv venv
   ```

2. **Activate the Virtual Environment**
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   ```sh
   touch .env  # Create an environment file
   ```
   Add your own API keys or environment variables inside the `.env` file. However for this assignment i have included my gemini api key for a free tier account for easy testing.

5. **Run the FastAPI Server**
   ```sh
   python3 main.py
   ```

6. **Access the API**
   - The server should now be running. By default, you can access it at:
     ```
     http://0.0.0.0:8000
     ```
   - To view the interactive API documentation, open:
     ```
     http://0.0.0.0:8000/docs
     ```

This will enable auto-reloading and allow access from external devices.

## Troubleshooting
- If you face issues with dependencies, ensure `requirements.txt` is correctly formatted.
- Use `pip freeze > requirements.txt` to update dependencies if needed.
- Check logs for errors when running the server.
