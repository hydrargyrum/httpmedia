FROM docker.io/python:3-slim AS wsgiref

RUN useradd --create-home httpmedia
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ffmpegthumbnailer

COPY pyproject.toml /src/
COPY httpmedia/ /src/httpmedia/
COPY README.md /src/

USER httpmedia
WORKDIR /home/httpmedia

RUN python3 -m pip install /src

CMD python3 -m httpmedia

EXPOSE 8000
VOLUME /media
VOLUME /home/httpmedia/.cache/thumbnails

FROM wsgiref AS gunicorn

RUN python3 -m pip install gunicorn

CMD HTTPMEDIA_ROOT=/media python3 -m gunicorn --bind=0.0.0.0:8000 --access-logfile=- --name=httpmedia httpmedia.wsgi
