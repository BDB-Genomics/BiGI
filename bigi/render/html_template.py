import pkgutil

def load_template() -> str:
    """Loads the HTML template from the companion template.html file."""
    try:
        data = pkgutil.get_data("bigi.render", "template.html")
        if data is None:
            raise FileNotFoundError("pkgutil.get_data returned None")
        return data.decode("utf-8")
    except Exception as e:
        # Fallback if somehow not packaged
        return f"<html><body><h1>Error: template.html not found.</h1><p>Please reinstall BiGI.</p><p>Details: {e}</p></body></html>"

# Expose as a constant for backwards compatibility with cli.py
HTML_TEMPLATE = load_template()
