FROM debian:bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install utilities
RUN apt update && apt-get install -y --no-install-recommends python3-pip

# Set the working directory inside the container
WORKDIR /app

# Install python libraries
ADD dist/iris /app
ADD dist/wheels /app/wheels
RUN pip install --break-system-packages /app/wheels/*
RUN rm -rf /app/wheels

CMD ["python3", "main.py"]
