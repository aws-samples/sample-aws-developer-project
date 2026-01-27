# Use an official Python runtime as a base image
FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app
# Expose the port your Flask app listens on
EXPOSE 5000

RUN adduser --system appuser 
RUN chown -R appuser /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Copy the entire application code into the container
COPY . .

USER appuser
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --retries=3  CMD curl -f http://localhost:5000 || exit 1
