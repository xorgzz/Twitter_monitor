import subprocess
import sys
import os
import threading
import requests
import zipfile
import config
import time

libs = ["selenium"]

def process_lib(semaphore, lib) -> None:
	semaphore.acquire()
	
	try:
		__import__(lib)
	except ModuleNotFoundError:
		with open(os.devnull, "w") as devnull:
			print(f"Instalacja brakującej biblioteki - {lib}")
			if os.name == "posix":
				subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--break-system-packages", "--no-warn-script-location"], stdout=devnull, stderr=subprocess.STDOUT)
			else:
				subprocess.check_call([sys.executable, "-m", "pip", "install", lib], stdout=devnull, stderr=subprocess.STDOUT)

	semaphore.release()

def check_libs() -> None:
	semaphore = threading.Semaphore(4)
	threads = []
	for lib in libs:
		thread = threading.Thread(target=process_lib, args=(semaphore, lib,))
		thread.start()
		threads.append(thread)

	for t in threads:
		t.join()
		
def check_webdriver() -> None:
	os.makedirs(f"{config.PATH}{config.SLASH}webdriver", exist_ok=True)
	os.makedirs(f"{config.PATH}{config.SLASH}tweet_dump", exist_ok=True)

	if os.name == "posix":
		if not "geckodriver" in os.listdir(f"{config.PATH}{config.SLASH}webdriver"):
			resp = requests.get("https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip")
			if resp.status_code == 200:
				with open(f"{config.PATH}{config.SLASH}webdriver{config.SLASH}chromedriver.zip", "wb") as fp:
					fp.write(resp.content)
			else:
				print("Nie można pobrać webdrivera !!")
	else:
		if not "geckodriver.exe" in os.listdir(f"{config.PATH}{config.SLASH}webdriver"):
			resp = requests.get("https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-win64.zip")
			if resp.status_code == 200:
				with open(f"{config.PATH}{config.SLASH}webdriver{config.SLASH}geckodriver.zip", "wb") as fp:
					fp.write(resp.content)
			else:
				print("Nie można pobrać webdrivera !!")
	
	with zipfile.ZipFile(f"{config.PATH}{config.SLASH}webdriver{config.SLASH}geckodriver.zip", 'r') as zip_ref:
   		zip_ref.extractall(f"{config.PATH}{config.SLASH}webdriver")


def start_app() -> None:
	subprocess.check_call([sys.executable, f"{config.PATH}{config.SLASH}app.py"])

def main() -> None:
	os.system("clear" if os.name == "posix" else "cls")
	check_libs()
	os.system("clear" if os.name == "posix" else "cls")
	check_webdriver()
	os.system("clear" if os.name == "posix" else "cls")
	time.sleep(1.5)
	start_app()

if __name__ == '__main__':
	print("Starting...")
	main()