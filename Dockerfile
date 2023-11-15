FROM ghcr.io/ninjineers-2383/opencv-python:4.8.1-py3.11.6

# Add v4l2src plugin
RUN apt-get update; \
    apt-get install -y \
    gstreamer1.0-plugins-good;

WORKDIR /northstar

RUN pip3 install --find-links=https://tortall.net/~robotpy/wheels/2023/raspbian/ robotpy==2023.4.3.1

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt --extra-index-url https://www.piwheels.org/simple

# Path: /app
COPY . .

CMD ["python", "__init__.py"]
