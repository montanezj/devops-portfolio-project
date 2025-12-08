# 1. Start with a lightweight Linux OS that already has Python installed
FROM python:3.9-slim

# 2. Create a folder inside the container to hold our app
WORKDIR /app

# 3. Copy our current folder files (app.py) into that container folder
COPY . .

# 4. Run the command to install Flask inside the container
RUN pip install flask psutil

# 5. Tell the container what command to run when it starts up
CMD ["python", "app.py"]