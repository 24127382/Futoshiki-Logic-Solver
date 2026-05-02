"""
Reflex configuration for the Futoshiki Solver GUI.
"""
import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="gui",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    log_level="debug",
    disable_plugins=[SitemapPlugin],
)
