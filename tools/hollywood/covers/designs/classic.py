"""The current house cover (tools/hollywood/hollywood.py), for reference."""
import sys
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", ".."))
import hollywood
import lib


def render(m):
    mm = hollywood._meta(m)
    mm["instrumentation"] = [tuple(x) for x in m["instrumentation"]]
    css = hollywood.CSS.replace("@page { size: 11in 17in; margin: 0; }", "")
    return lib.page(css, hollywood.cover_html(mm)[len("\n<div class='page cover'>"):-len("</div>")],
                    "classic").replace("<div class='page'>", "<div class='page cover'>", 1)
