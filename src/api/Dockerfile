FROM python:3.11.4

# Setup a spot for the api code
WORKDIR /usr/local/src

ARG GITHUB_ACCESS_TOKEN

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
COPY api/requirements.txt .

RUN pip install -r requirements.txt


# Copy over the source code
COPY api api
COPY main.py main.py

# Kick things off
ENTRYPOINT [ "uvicorn" ]
CMD ["main:app", "--host", "0.0.0.0"]
