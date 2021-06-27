# Use slim-buster instead of alpine for better performance
FROM python:slim-buster

# Add flaskapi user without password and with default settings
RUN adduser --disabled-password --gecos '' flaskapi

# Set the working dir to the newly created /home/flaskapi after the user added
WORKDIR /home/flaskapi

# Copy the requirements.txt, create the virtual environment and install all dependencies
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt --no-cache-dir

# Copy all other files to the image
COPY . .

# Make sure boot.sh is executable
RUN chmod +x boot.sh

# Change the owner of all files in the work dir to flaskapi
RUN chown -R flaskapi:flaskapi ./

# Set the FLASK_APP environment to the flaskAPI.py
ENV FLASK_APP flaskAPI.py

# Make sure to use /bin/bash to run .sh file
ENTRYPOINT [ "/bin/bash", "boot.sh" ]