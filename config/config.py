from pathlib import Path

def load_env():
    env_path = Path(__file__).resolve().parent / ".env"
    config = {}

    for line in env_path.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip()

    return config
