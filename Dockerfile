# Use an official Python runtime as a parent image (slim is good for size)
FROM python:3.11-slim

# Set environment variables for best practices
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents python from writing .pyc files
ENV PYTHONUNBUFFERED 1      # Force stdout/stderr streams to be unbuffered

# Set the working directory in the container
WORKDIR /opt/app

# --- PyTorch Installation ---
# Install specific CPU versions of PyTorch and TorchVision first.
# Using the CPU-specific index avoids pulling larger GPU dependencies.
# Ensure these versions are compatible with your model checkpoint.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision

# --- Application Dependencies ---
# Copy the requirements file into the container FIRST to leverage Docker caching
COPY requirements.txt .

# Install application dependencies from requirements.txt
# IMPORTANT: For efficiency and to avoid version conflicts, it's best if 'torch' and 'torchvision'
# are EITHER NOT listed in requirements.txt OR list the EXACT versions installed above (2.4.1/0.19.1).
# Common dependencies needed here: Flask, Pillow, gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# Copy necessary application files and directories into the container's working directory (/opt/app)
# Adjust these lines if your file/folder names are different.
COPY app.py .
COPY image_transformations.py .
# Uncomment the next line if endpoint_validation.py exists and is needed for runtime
# COPY endpoint_validation.py .
COPY templates ./templates/
COPY model ./model/
# If you created a 'static' folder for CSS/JS (instead of inline/CDN), uncomment the next line
# COPY static ./static/

# --- Security: Run as Non-Root User ---
# Create a non-root user and group for security
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser -m appuser

# Change ownership of the app directory to the new user
# Use /opt/app explicitly for clarity
RUN chown -R appuser:appuser /opt/app

# Switch context to the non-root user
USER appuser

# --- Networking ---
# Expose the port the app runs on (matching the Gunicorn command)
EXPOSE 8000

# --- Run Command ---
# Use Gunicorn to run the Flask app ('app:app' means look for the 'app' instance in 'app.py')
# --preload loads the application code before forking workers (can save memory, check compatibility)
# Adjust the number of workers (-w) based on server resources (e.g., 2 * num_cores + 1 is a common guideline)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--preload", "app:app"]