import os

def load_template() -> str:
    """Loads the HTML template from the companion template.html file."""
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback if somehow not packaged
        return "<html><body><h1>Error: template.html not found.</h1><p>Please reinstall BiGI.</p></body></html>"

# Expose as a constant for backwards compatibility with cli.py
HTML_TEMPLATE = load_template()
