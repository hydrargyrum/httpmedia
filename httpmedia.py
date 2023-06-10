#!/usr/bin/env python3
# license: WTFPLv2

"""
Shares a directory on HTTP like "python3 -m http.server" but is capable of
handling "Range" header, making it suitable for seeking randomly in medias.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
from secrets import token_hex
from wsgiref.simple_server import WSGIServer

import bottle
from bottle import (
    route, run, abort, static_file, WSGIRefServer, redirect, template, install,
    request, HTTPError,
)
import jwt
import vignette


JWT_SECRET = token_hex()


class BasicAuthPlugin:
    api = 2
    name = "require-basic-auth"

    def __init__(self, required_auth):
        if required_auth is not None:
            # just check type
            _, _ = required_auth
        self.required_auth = required_auth

    def setup(self, app):
        pass

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            if self.required_auth and request.auth != self.required_auth:
                return HTTPError(
                    401, 'Authentication required',
                    **{'WWW-Authenticate': 'Basic realm="Private"'}
                )
            return callback(*args, **kwargs)

        return wrapper


@route('/static/<file>')
def get_static(file):
    return static_file(file, str(Path(__file__).parent / 'static'))


@route('/thumb/<token>')
def get_thumb(token):
    if not vignette:
        abort(404)

    try:
        orig = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.exceptions.InvalidTokenError:
        abort(403)
    name = orig['t']

    dir = Path(vignette._thumb_path_prefix()) / 'large'
    return static_file(name, str(dir))


def build_thumb(sub):
    if not sub.is_dir():
        thumb = vignette.get_thumbnail(str(sub), size='large')
        if thumb:
            thumb = Path(thumb)
            return jwt.encode({'t': thumb.name}, JWT_SECRET, algorithm="HS256")


@route('/')
@route('/<path:path>')
def anything(path='/'):
    try:
        target = ROOT.joinpath(path.lstrip('/')).resolve(True)
        relative = target.relative_to(ROOT)
    except (FileNotFoundError, ValueError):
        abort(403)

    def sortfiles(p):
        return p.name

    if request.query.get("sort") == "mtime":
        def sortfiles(p):
            return -p.stat().st_mtime

    if target.is_dir():
        if not path.endswith('/'):
            redirect(f'{path}/')

        items = {
            sub: build_thumb(sub)
            for sub in sorted(target.iterdir(), key=sortfiles)
        }

        return template('base.tpl', items=items, base_url=BASE_URL)
    elif target.is_file():
        return static_file(str(relative), str(ROOT))

    abort(404)


class ThreadingMixIn:
    # builtin socketserver.ThreadingMixIn has a memory leak: https://bugs.python.org/issue37193
    # let's use a thread pool to fix it for now
    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        pool.submit(self.process_request_thread, request, client_address)


class ThreadedServer(ThreadingMixIn, WSGIServer):
    pass


def parse_auth(s):
    if s == "env":
        try:
            return (
                os.environ["HTTPMEDIA_USER"],
                os.environ["HTTPMEDIA_PASSWORD"]
            )
        except KeyError:
            raise ValueError(
                "Missing HTTPMEDIA_USER or HTTPMEDIA_PASSWORD"
            )
    user, sep, password = s.partition(":")
    if not sep:
        raise ValueError("Format is USER:PASSWORD")
    return (user, password)


def main():
    global ROOT, pool

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bind', '-b', default='', metavar='ADDRESS',
        help='Specify alternate bind address '
        '[default: all interfaces]'
    )
    parser.add_argument(
        '--directory', '-d', default=Path.cwd(), type=Path,
        help='Specify alternative directory '
        '[default:current directory]'
    )
    parser.add_argument(
        '--auth', metavar='USER:PASSWORD', type=parse_auth,
        help='Require HTTP authentication',
    )
    parser.add_argument(
        'port', action='store',
        default=8000, type=int,
        nargs='?',
        help='Specify alternate port [default: 8000]'
    )
    args = parser.parse_args()

    ROOT = args.directory
    bottle.TEMPLATE_PATH = [str(Path(__file__).with_name('views'))]

    install(BasicAuthPlugin(args.auth))

    with ThreadPoolExecutor() as pool:
        run(server=WSGIRefServer(host=args.bind, port=args.port, server_class=ThreadedServer))


bottle.TEMPLATE_PATH = [str(Path(__file__).with_name('views'))]
BASE_URL = os.environ.get("HTTPMEDIA_BASEURL", "")

if __name__ == "__main__":
    main()
else:
    ROOT = Path(os.environ["HTTPMEDIA_ROOT"])
    application = bottle.default_app()
