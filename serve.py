"""Start the local app and open its page on Windows, macOS, or Linux."""
from pathlib import Path
import os
import json
import socket
import threading
import webbrowser

from frontend import build_frontend


def reserve_socket(preferred_port=8000):
    """Reserve our own listener; an occupied port must never open an old app."""
    for port in range(preferred_port, min(preferred_port + 20, 65536)):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            listener.bind(('127.0.0.1', port))
            listener.listen(128)
            listener.setblocking(False)
            return listener
        except OSError as exc:
            listener.close()
            error_code = getattr(exc, 'winerror', None) or exc.errno
            if error_code not in (48, 98, 10048, 13, 10013):
                raise
    raise SystemExit(f'No available local port from {preferred_port} to {min(preferred_port + 19, 65535)}. Close a previous TrustLens window and try again.')


def announce_when_ready(server, url, stopped, open_browser):
    while not stopped.wait(0.05):
        if server.started:
            print(f'\nTrustLens is ready: {url}\nUse this new address. Keep this window open. Press Ctrl+C to stop.', flush=True)
            if open_browser is not None:
                open_browser(url)
            return


def main():
    os.chdir(Path(__file__).resolve().parent)
    local = Path('local-runtime.json')
    if local.is_file():
        allowed = {'TRUSTLENS_CLIP_CACHE', 'TRUSTLENS_COMMUNITY_WEIGHTS', 'TRUSTLENS_CREDENTIALS_PYTHON', 'TRUSTLENS_DEVICE'}
        for key, value in json.loads(local.read_text(encoding='utf-8')).items():
            if key in allowed:
                os.environ.setdefault(key, str(value))
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    try:
        import uvicorn
    except ImportError:
        raise SystemExit('Install the web dependencies first: python -m pip install -r requirements.txt')
    build_frontend()
    listener = reserve_socket(8765)
    port = listener.getsockname()[1]
    url = f'http://127.0.0.1:{port}/'
    print(f'Starting the updated TrustLens at {url}', flush=True)
    if port != 8765:
        print('The preferred port is occupied. This launch uses its own available port.', flush=True)
    server = uvicorn.Server(uvicorn.Config('app.main:app', host='127.0.0.1', port=port))
    stopped = threading.Event()
    opener = None if os.environ.get('TRUSTLENS_NO_BROWSER') == '1' else webbrowser.open
    watcher = threading.Thread(target=announce_when_ready, args=(server, url, stopped, opener), daemon=True)
    watcher.start()
    try:
        server.run(sockets=[listener])
    finally:
        stopped.set()
        watcher.join(timeout=1)
        listener.close()
    if not server.started:
        raise SystemExit('TrustLens did not finish starting. See the error above.')


if __name__ == '__main__':
    main()
