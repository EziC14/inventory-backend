FROM python:3.12-alpine

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN apk add --no-cache \
    ca-certificates \
    gcc \
    postgresql-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    git \
    python3-dev \
    musl-dev

RUN pip install -r requirements.txt --root-user-action=ignore

COPY . .
EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]