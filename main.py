
import argparse, asyncio
from scrape_linkedin import scrape
from apply_runner import run_apply
from email_watcher import run as watch_mail

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["scrape", "apply", "watch"])
    args = parser.parse_args()

    if args.cmd == "scrape":
        asyncio.run(scrape())
    elif args.cmd == "apply":
        asyncio.run(run_apply())
    elif args.cmd == "watch":
        watch_mail()

if __name__ == "__main__":
    main()
