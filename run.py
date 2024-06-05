import argparse
from apps import create_app

def main():
    parser = argparse.ArgumentParser(description="Run the web application.")
    parser.add_argument(
        "-m", "--mode", type=str, default="default", help="Mode in which to run the app, MODE: default, develop, test"
    )
    args = parser.parse_args()
    
    app = create_app(mode=args.mode)
    app.run()

if __name__ == "__main__":
    main()