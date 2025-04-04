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


__version__ = "0.3.0"


class BasicAuthPlugin:
    api = 2
    name = "require-basic-auth"

    def __init__(self, required_auth, realm="Private"):
        if required_auth is not None:
            # just check type
            _, _ = required_auth
        self.required_auth = required_auth
        self.realm = realm

    def setup(self, app):
        pass

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            if self.required_auth and request.auth != self.required_auth:
                realm = self.realm.replace('"', '')  # a bit rough
                return HTTPError(
                    401, 'Authentication required',
                    **{'WWW-Authenticate': 'Basic realm="%s"' % realm}
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

    if "t" in orig:
        name = orig['t']
        dir = Path(vignette._thumb_path_prefix()) / 'large'
    elif "r" in orig:
        thumb = vignette.get_thumbnail(str(ROOT / orig["r"]))
        if not thumb:
            abort(404)
        thumb = Path(thumb)
        name = thumb.name
        dir = str(thumb.parent)

    return static_file(name, str(dir))


def build_thumb(sub, reqpath):
    if not sub.is_dir():
        thumb = vignette.try_get_thumbnail(str(sub), size='large')
        if thumb:
            # thumb already exists, use it
            to_encode = {"t": Path(thumb).name}
        else:
            # try to generate it later: when client tries to load image
            to_encode = {"r": str(reqpath)}
        return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


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
        def sortfiles(p):  # noqa
            return -p.stat().st_mtime

    if target.is_dir():
        if not path.endswith('/'):
            redirect(f'{path}/')

        items = {
            sub: build_thumb(sub, sub.relative_to(ROOT))
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
        help='Specify alternate bind address [default: all interfaces]'
    )
    parser.add_argument(
        '--directory', '-d',
        help='Specify directory [default:current directory] env: HTTPMEDIA_ROOT'
    )
    parser.add_argument(
        '--auth', metavar='USER:PASSWORD', type=parse_auth,
        help='Require HTTP authentication',
    )
    parser.add_argument(
        '--auth-realm', metavar='REALM', default="Private",
        help='Realm text for HTTP authentication',
    )
    parser.add_argument(
        'port', action='store',
        default=8000, type=int,
        nargs='?',
        help='Specify alternate port [default: 8000]'
    )
    args = parser.parse_args()

    ROOT = Path(args.directory or os.environ.get("HTTPMEDIA_ROOT") or Path.cwd())
    ROOT = ROOT.resolve(strict=True)

    install(BasicAuthPlugin(args.auth, args.auth_realm))

    with ThreadPoolExecutor() as pool:
        run(server=WSGIRefServer(host=args.bind, port=args.port, server_class=ThreadedServer))


bottle.TEMPLATE_PATH = [str(Path(__file__).with_name('views'))]
BASE_URL = os.environ.get("HTTPMEDIA_BASEURL", "")
JWT_SECRET = os.environ.get("HTTPMEDIA_SECRET", token_hex())


if __name__ == "__main__":
    main()
