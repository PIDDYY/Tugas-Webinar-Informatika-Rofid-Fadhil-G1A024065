"""Server lokal tanpa framework untuk membuka dashboard Webinar 5."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from pathlib import Path
import argparse

BASE_DIR = Path(__file__).resolve().parent


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(302)
            self.send_header('Location', '/web/index.html')
            self.end_headers()
            return
        return super().do_GET()


def main():
    parser = argparse.ArgumentParser(description='Server lokal dashboard HCI dan visualisasi data')
    parser.add_argument('--port', type=int, default=8000, help='Port HTTP lokal (default: 8000)')
    args = parser.parse_args()
    handler = partial(DashboardHandler, directory=str(BASE_DIR))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as httpd:
        print(f'Dashboard tersedia di http://localhost:{args.port}/')
        print('Tekan Ctrl+C untuk menghentikan server.')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer dihentikan.')


if __name__ == '__main__':
    main()
