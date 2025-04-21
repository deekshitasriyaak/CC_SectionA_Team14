FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    apt-get clean

# Copy the application code
COPY . /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set the command to run the application
CMD ["python", "run.py"]