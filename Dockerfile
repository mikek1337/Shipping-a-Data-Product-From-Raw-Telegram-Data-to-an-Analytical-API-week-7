# Use a lightweight Python base image. Python 3.9 is chosen for broad compatibility.
FROM python:3.9-slim-buster

# Set the working directory inside the container. All subsequent commands will run from here.
WORKDIR /app

# Copy the requirements.txt file first. This allows Docker to cache the dependency installation
# if requirements.txt doesn't change, speeding up subsequent builds.
COPY requirements.txt .

# Install Python dependencies from requirements.txt.
# --no-cache-dir prevents pip from storing cache, reducing image size.
RUN pip install --no-cache-dir -r requirements.txt

# Install dbt-postgres, the adapter for connecting dbt to PostgreSQL.
RUN pip install --no-cache-dir dbt-postgres

# Copy the rest of your project files into the container.
# This includes your `script/`, `src/`, `config.ini`, and the `telegram_analysis/` dbt project.
COPY . .

# Set environment variables for Telegram API and PostgreSQL.
# These are placeholders. You MUST provide actual values when running the Docker container
# using the `-e` flag (e.g., `docker run -e APP_ID=...`).
# These variables will be used by your Python scripts and by dbt's profiles.yml.
ENV APP_ID="" \
    APP_KEY="" \
    PHONE="" \
    HOST="" \
    PASSWORD="" \
    USERNAME="" \
    PORT="" \
    DATABASE=""

# Create necessary directories for scraped raw data and logs.
# This ensures the `script/scrapy.py` can write its output.
RUN mkdir -p data/raw/telegram-messages data/raw/telegram-images logs

# Define the command to run when the container starts.
# This uses `/bin/bash -c` to allow chaining multiple commands.
# The commands are executed in the sequence of your pipeline: scrape, load, test dbt, run dbt.
CMD ["/bin/bash", "-c", "\
    echo 'Starting Telegram scraping...'; \
    cd my_project/ && fastapi dev &\
    cd ../scripts && dagster dev -f pipeline.py\
    "]

EXPOSE 8000
EXPOSE 3000

