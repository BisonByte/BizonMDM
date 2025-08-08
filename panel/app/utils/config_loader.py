import os
import configparser

def load_config():
    """Load configuration from config.ini. If missing, return pre-install mode."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
    config_path = os.path.abspath(config_path)
    parser = configparser.ConfigParser()
    if not os.path.exists(config_path):
        return {"INSTALLED": False, "APP_URL": None}
    parser.read(config_path)
    cfg = {s: dict(parser.items(s)) for s in parser.sections()}
    # Flatten for simplicity
    flat = {}
    for section, values in cfg.items():
        for k, v in values.items():
            flat[f"{k.upper()}"] = v
    flat['INSTALLED'] = flat.get('INSTALLED', '0') == '1'

    # Extra defense: consider installation flag file
    flag_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.installed'))
    if os.path.exists(flag_path):
        flat['INSTALLED'] = True
    return flat
