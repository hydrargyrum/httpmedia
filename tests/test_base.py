#!/usr/bin/env pytest

import random
from socket import create_connection
import subprocess
import sys
import time
from urllib.request import urlopen, HTTPError

import pytest


PORT = random.randrange(10000, 65000)


def request(url):
    try:
        response = urlopen(url)
    except HTTPError as exc:
        return exc.status, exc.headers, exc.fp.read()
    return response.status, response.headers, response.read()


@pytest.fixture(scope="module")
def server():
    cmd = [sys.executable, "-m", "httpmedia", str(PORT)]
    with subprocess.Popen(cmd) as proc:
        for _ in range(20):
            assert proc.poll() is None
            time.sleep(.1)
            try:
                with create_connection(("localhost", PORT), timeout=.1):
                    break
            except ConnectionRefusedError:
                pass
        else:
            proc.terminate()
            raise TimeoutError(f"'localhost:{PORT}' did not respond")

        yield proc
        proc.terminate()


def test_index(server):
    status, headers, body = request(f"http://localhost:{PORT}/")
    assert status == 200
    body = body.decode()
    assert "README.md" in body
    assert ".gitattributes" not in body


def test_file(server):
    status, headers, body = request(f"http://localhost:{PORT}/tests/test_base.py")
    assert status == 200
    assert body.decode().startswith("#!/usr/bin/env pytest")


def test_hidden(server):
    status, headers, body = request(f"http://localhost:{PORT}/.gitattributes")
    assert status == 403
