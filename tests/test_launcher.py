import errno
import threading
from types import SimpleNamespace

import pytest

import serve
from frontend import STATIC, render_frontend, build_frontend


def test_packaged_page_is_self_contained_even_for_older_file_servers():
    build_frontend()
    html = (STATIC / 'index.html').read_text(encoding='utf-8')
    assert html == render_frontend()
    assert '<style>:root' in html
    assert "<script>'use strict';" in html
    assert 'src="/static/app.js"' not in html
    assert 'href="/static/styles.css"' not in html
    assert 'src="/static/mode-route.js"' not in html
    assert 'src="/static/learning-practice.js"' not in html
    assert 'href="/static/learning-practice.css"' not in html
    assert "const LearningPractice=" in html
    assert '\u00e2\u20ac' not in html
    assert '\u00c2\u00b7' not in html


def test_launcher_reserves_a_different_port_when_occupied(monkeypatch):
    listeners = []

    class Listener:
        def __init__(self, *args):
            self.closed = False
            listeners.append(self)
        def setsockopt(self, *args):
            pass
        def bind(self, address):
            self.address = address
            if address[1] == 8000:
                raise OSError(errno.EADDRINUSE, 'Occupied by old server')
        def listen(self, backlog):
            pass
        def setblocking(self, enabled):
            pass
        def close(self):
            self.closed = True

    monkeypatch.setattr(serve.socket, 'socket', Listener)
    listener = serve.reserve_socket()
    assert listener.address == ('127.0.0.1', 8001)
    assert listeners[0].closed


def test_unexpected_binding_error_is_not_hidden(monkeypatch):
    class Listener:
        closed = False
        def setsockopt(self, *args):
            pass
        def bind(self, address):
            raise OSError(errno.EINVAL, 'Invalid configuration')
        def close(self):
            self.closed = True
    listener = Listener()
    monkeypatch.setattr(serve.socket, 'socket', lambda *args: listener)
    with pytest.raises(OSError, match='Invalid configuration'):
        serve.reserve_socket()
    assert listener.closed


def test_browser_opens_only_after_this_server_starts():
    server = SimpleNamespace(started=False)
    stopped = threading.Event()
    opened = threading.Event()
    addresses = []
    def opener(url):
        addresses.append(url)
        opened.set()
    watcher = threading.Thread(target=serve.announce_when_ready,
        args=(server, 'http://127.0.0.1:8001/', stopped, opener))
    watcher.start()
    try:
        assert not opened.wait(0.15)
        server.started = True
        assert opened.wait(2)
        assert addresses == ['http://127.0.0.1:8001/']
    finally:
        stopped.set()
        watcher.join(timeout=2)
    assert not watcher.is_alive()


def test_failed_start_does_not_open_any_page():
    stopped = threading.Event()
    stopped.set()
    addresses = []
    serve.announce_when_ready(SimpleNamespace(started=False),
        'http://127.0.0.1:8000/', stopped, addresses.append)
    assert addresses == []
