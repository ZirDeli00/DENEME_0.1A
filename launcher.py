"""Hakan ÇELİK sohbet uygulaması için HTML başlatıcı."""
from pathlib import Path
import webbrowser


def main() -> None:
    html_path = Path(__file__).with_name("Hakan_CELIK_Chat.html").resolve()
    webbrowser.open(html_path.as_uri())


if __name__ == "__main__":
    main()
