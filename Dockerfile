# Use an official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory's contents into the container
COPY . /app
COPY ./flaskr/schema.sql /app/schema.sql

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable to point to your Flask app
ENV FLASK_APP=flaskr

# Expose the Flask default port
EXPOSE 5000

# Command to run the app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]