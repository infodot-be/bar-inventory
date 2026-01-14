FROM python:3.13-slim AS builder
ENV TZ Europe/Brussels
RUN echo Europe/Brussels >/etc/timezone && dpkg-reconfigure -f noninteractive tzdata

# Install build dependencies for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
ADD requirements.txt /
# install the dependencies and packages in the requirements file
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r /requirements.txt


# final stage
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Brussels
RUN echo Europe/Brussels >/etc/timezone && dpkg-reconfigure -f noninteractive tzdata

# Install runtime dependencies for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /
VOLUME /socket
VOLUME /media
VOLUME /static
VOLUME /backup
RUN mkdir /etc/gunicorn.d/
# ADD gunicorn/ /etc/gunicorn.d/

ADD code/ /code
# RUN chmod +x /code/schedule.py
CMD ["/usr/local/bin/gunicorn", "--bind", "unix:/socket/gunicorn.socket", "--chdir", "/code", "--config", "/etc/gunicorn.d/gunicorn.py", "web.wsgi_prod:application"]
