FROM python:3.9-bullseye

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN echo "alias ll='ls -alF'" >> ~/.bashrc && \
    echo "alias la='ls -A'" >> ~/.bashrc && \
    echo "alias l='ls -CF'" >> ~/.bashrc

WORKDIR /opt/project
