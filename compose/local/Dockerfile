FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Setup SSH with secure root login, this is for development only
RUN apt-get update 
RUN apt-get install -y openssh-server netcat-traditional \
 && mkdir /var/run/sshd \
 && echo 'root:password' | chpasswd \
 && sed -i 's/\#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Install system dependencies for PostgreSQL
RUN apt-get install -y \
    libpq-dev \
    gcc 

# install system dependencies for unstructured
RUN apt-get install -y \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    qpdf \
    libreoffice \
    pandoc
 
RUN rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./compose/local/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/local/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh

# Copy the entire Django project to the working directory in the container
COPY ./cerebrix /app/

WORKDIR /app

ENTRYPOINT [ "/entrypoint.sh" ]