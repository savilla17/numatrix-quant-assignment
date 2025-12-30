import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

print("API KEY:", os.getenv("IYI2voSbj52XgEeos3H314QjM8cyjHwb6jH6H23BooO7sBc8IJJ7flNjX73c2FEl"))
print("SECRET :", os.getenv("G2yHKEBL9yoF0bqJEllCGTgtTQkWaPGCn5LnCtnFqIphPcDfO9Mz2ClXL2KqlowL"))
