# DOCKERFILE TO LAUNCH THE MICRO-SERVICE

# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Upgrade pip if necessary
RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY showcase /app/showcase
COPY svc/main.py /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "--host", "0.0.0.0", "main:rootapp"]