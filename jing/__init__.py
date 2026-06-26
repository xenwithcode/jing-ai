"""
JING — The Expert Spirit for the Modern Artisan
"""

__version__ = "0.1.0"
__author__ = "Xavier"
__description__ = "The Expert Spirit for the Modern Artisan"
__license__ = "MIT"

PROJECT_NAME = "JING"
PROJECT_TAGLINE = "The Expert Spirit for the Modern Artisan"
PROJECT_NAME_CN = "千问匠擎"
PROJECT_NAME_PINYIN = "Qiānwèn Jiàngqíng"


def get_version() -> str:
    return __version__


def _jing_art() -> str:
    rows = [
        ("JJJJJJ", "IIIIII", "N    N", "GGGGGG"),
        ("    JJ", "  II  ", "NN   N", "G     "),
        ("    JJ", "  II  ", "N N  N", "G  GGG"),
        ("    JJ", "  II  ", "N  N N", "G    G"),
        ("J   JJ", "  II  ", "N   NN", "GGGGGG"),
        ("  JJJJ", "IIIIII", "N    N", "GGGGGG"),
    ]
    padding = 58 - 3 - 33
    lines = []
    for j, i, n, g in rows:
        content = f"{j}   {i}   {n}   {g}"
        lines.append(f"║   {content}{'':>{padding}}║")
    return "\n".join(lines)


def banner() -> str:
    return f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
{_jing_art()}
║                                                          ║
║   {PROJECT_TAGLINE:<54}║
║   v{__version__:<56}║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


def main() -> None:
    print(banner())
