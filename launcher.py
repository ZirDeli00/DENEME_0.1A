import http.server
import os
import socketserver
import threading
import time
import webbrowser

PORT = 4173
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)


def main() -> None:
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        threading.Thread(target=lambda: (time.sleep(0.6), webbrowser.open(url)), daemon=True).start()
        print(f"Flipy Bird acildi: {url}")
        print("Kapatmak icin bu pencereyi kapatin.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
