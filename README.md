# httpmedia

## What is it?

* Simple file-sharing on HTTP (like [`python -m http.server`](https://docs.python.org/3/library/http.server.html#http-server-cli) on steroids)
* Shows thumbnails for images/videos/others using [vignette](https://pypi.org/project/vignette/)
* Supports audio/video file seeking (`python -m http.server` does not!)
* Can display a slideshow using [baguettebox](https://feimosi.github.io/baguetteBox.js/)
* HTTP basic auth for access protection
* Few [dependencies](https://gitlab.com/hydrargyrum/httpmedia/-/blob/main/requirements.txt)
* Free license ([WTFPLv2](http://www.wtfpl.net/))
* Usable through WSGI or standalone

## Install

From [PyPI](https://pypi.org/project/httpmedia/):

```
pipx install httpmedia
```

## Configuration

### Command-line arguments (not for WSGI)

- `--bind=ADDRESS`
- `--root=DIR`: more prioritary than `$HTTPMEDIA_ROOT` if present, defaults to current directory if neither is set
- `--auth=USER:PASSWORD`: protect with HTTP basic auth
- `--auth=env`: same as above but fetch credentials from `$HTTPMEDIA_USER` and `$HTTPMEDIA_PASSWORD`
- `--auth-realm=REALM`: HTTP basic auth realm (can be useful to distinguish different auths on the same host)
- `PORT`

### Env vars (typically for WSGI)

- `HTTPMEDIA_ROOT`: directory to be published
- `HTTPMEDIA_BASEURL`: useful when reverse proxied, thumbnails and static resources will be refered to be under that base url so request are directed to httpmedia by the reverse proxy

## Run in a container

    podman build -t localhost/httpmedia -f Containerfile
    podman run --rm -n httpmedia -v /your/files:/media -p 8000:8000 -e HTTPMEDIA_BASEURL=https://your.example/medias/ localhost/media
