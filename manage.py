"""管理脚本"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.screenshot import cleanup_old_outputs
from app.config import Config

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="run")
    parser.add_argument("--port", type=int, default=18083)
    args = parser.parse_args()

    if args.command == "cleanup":
        cleanup_old_outputs(Config.OUTPUT_FOLDER, max_age_hours=1)
        print("清理完成")
    else:
        app = create_app()
        app.run(host="0.0.0.0", port=args.port, debug=True)
