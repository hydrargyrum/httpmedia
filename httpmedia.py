#!/usr/bin/env python3
# license: WTFPLv2

"""
Shares a directory on HTTP like "python3 -m http.server" but is capable of
handling "Range" header, making it suitable for seeking randomly in medias.
"""

import argparse
from pathlib import Path
from socketserver import ThreadingMixIn
from urllib.parse import quote
from wsgiref.simple_server import WSGIServer

from bottle import route, run, abort, static_file, WSGIRefServer, redirect
import vignette


DIR = """<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static/style.css" />
<script src="/static/slideshow.css"></script>
</head>
<body>
{0}
</body>
</html>
"""


def build_link(sub):
    link = None
    thumb = None

    if not sub.is_dir():
        thumb = vignette.get_thumbnail(str(sub), size='large')
    if thumb:
        thumb = Path(thumb)
        link = f'''
            <div class="item">
                <a href="{quote(sub.name)}">
                    <img class="thumbnail" src="/thumb/{thumb.name}" />
                    <span class="label">
                        {sub.name}
                    </span>
                </a>
            </div>
        '''

    if not link:
        link = f'''
            <div class="item">
                <a href="{quote(sub.name)}{"/" if sub.is_dir() else ""}">
                    <span class="label">
                        {sub.name}{"/" if sub.is_dir() else ""}
                    </span>
                </a>
            </div>
        '''

    return link


@route('/static/<file>')
def get_static(file):
    return static_file(file, str(Path(__file__).parent))


@route('/thumb/<name>')
def get_thumb(name):
    if not vignette:
        abort(404)

    dir = Path(vignette._thumb_path_prefix()) / 'large'
    return static_file(name, str(dir))


@route('/')
@route('/<path:path>')
def anything(path='/'):
    try:
        target = ROOT.joinpath(path.lstrip('/')).resolve(True)
        relative = target.relative_to(ROOT)
    except (FileNotFoundError, ValueError):
        abort(403)

    if target.is_dir():
        if not path.endswith('/'):
            redirect(f'{path}/')

        parts = [
            build_link(sub)
            for sub in sorted(target.iterdir())
        ]
        return DIR.format('\n'.join(parts))
    elif target.is_file():
        return static_file(str(relative), str(ROOT))

    abort(404)


class ThreadedServer(ThreadingMixIn, WSGIServer):
    pass


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
    'port', action='store',
    default=8000, type=int,
    nargs='?',
    help='Specify alternate port [default: 8000]'
)
args = parser.parse_args()

ROOT = args.directory
run(server=WSGIRefServer(host=args.bind, port=args.port, server_class=ThreadedServer))
