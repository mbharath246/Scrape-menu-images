import os
import subprocess

def main():
    # Run scraping_urls.py
    print("Running scraping_urls.py...")
    subprocess.run(["python", "scraping_urls.py"])
    print("scraping_urls.py executed successfully.")
    
    # Run store_database.py
    print("Running store_database.py...")
    subprocess.run(["python", "store_database.py"])
    print("store_database.py executed successfully.")

if __name__ == "__main__":
    main()
