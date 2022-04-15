# syntax=docker/dockerfile:1

# ^^^ Must be first line to work

# Use basic python image
FROM python:3.8-slim-buster

# Create dir
WORKDIR /sublimate

# Add user

# Copy over the requirements for pip
COPY requirements.txt requirements.txt
copy sublimate /sublimate/sublimate

# install the required packages
RUN pip3 install -r requirements.txt && \
    pip3 install markdown && \
    pip3 install md_mermaid && \
    pip3 install matplotlib && \
    pip3 install pdfkit && \
    pip3 install pandoc && \
    apt-get update && \
    apt-get install -y pandoc nodejs npm && \
    npm install --global mermaid-filter --ignore-scripts --unsafe-perm=true


# Copy everything for sublimate to the container image
#COPY /.trivium /home/temp/.trivium

RUN useradd -m temp
USER temp

WORKDIR /out

# set sublimate.py as the entrypoint
ENTRYPOINT ["python","/sublimate/sublimate/sublimate.py"]
