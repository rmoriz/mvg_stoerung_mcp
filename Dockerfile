# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose the port the app runs on (if applicable, though MCP uses stdio)
# EXPOSE 8080

# Define environment variable for the server name
ENV MCP_SERVER_NAME=mvg-stoerung

# Run mvg_mcp_server.py when the container launches
CMD ["python", "mvg_mcp_server.py"]
