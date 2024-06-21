import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import config
import time
import re
import ipaddress

gecko_driver_path = f"{config.PATH}{config.SLASH}webdriver{config.SLASH}geckodriver" if os.name == "posix" else f"{config.PATH}{config.SLASH}webdriver{config.SLASH}geckodriver.exe"
sys.path.insert(0, gecko_driver_path)

options = Options()

if config.DEBUG_MODE == False:
	options.add_argument("--headless")

driver = webdriver.Firefox(options=options)


def is_valid_ip(ip) -> bool:
	try:
		ip = ipaddress.ip_address(ip)
		return not ip.is_private and not ip.is_reserved and not ip.is_loopback
	except ValueError:
		return False

def find_ip_or_link(text) -> str:
	ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
	url_pattern = re.compile(r'\bhttps?://[^\s/$.?#].[^\s]*\b', re.IGNORECASE)

	ip_match = ip_pattern.search(text)
	
	if ip_match:
		if is_valid_ip(ip_match.group()):
			return ip_match.group()

	url_match = url_pattern.search(text)

	if url_match:
		return url_match.group()

	return None

def get_tweets(user) -> None:
	short_sleep = 1
	print(f"\nRedirecting to @{user}")
	driver.get(f"https://x.com/{user}")
	time.sleep(2)

	# Scroll down to load newest tweets
	for i in range(1):
		scroll_height = driver.execute_script("return document.body.scrollHeight")
		time.sleep(short_sleep)
		driver.execute_script(f"window.scrollTo(0, {scroll_height});")
		time.sleep(short_sleep)

	tweets = driver.find_elements(By.XPATH, '//article[@role="article"]//div[@lang]')
	time.sleep(short_sleep)

	with open(f"{config.PATH}{config.SLASH}tweet_dump{config.SLASH}{user}.txt", "w") as fp:
		for tweet in tweets:
			text = str(tweet.text)
			out = find_ip_or_link(text)
			if out != None:
				print(out)
				fp.write(out)
				fp.write("\n")


def login_twitter() -> None:
	driver.get("https://twitter.com/login")
	print(f"Logging into account: {config.X_LOGIN}")
	
	time.sleep(5)

	username_field = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')
	username_field.send_keys(config.X_LOGIN)
	username_field.send_keys(Keys.RETURN)
	
	time.sleep(2)

	password_field = driver.find_element(By.XPATH, '//input[@name="password"]')
	password_field.send_keys(config.X_PASSWORD)
	password_field.send_keys(Keys.RETURN)
	
	time.sleep(2)	

	if driver.execute_script("return window.location.href;") == "https://x.com/home":
		print("Login Successful")
	else:
		print("Login Failed")
		driver.quit()
		sys.exit()


def main() -> None:
	try:
		login_twitter()
	except:
		print("Login Failed")
		driver.quit()
		sys.exit()

	for target in config.X_TARGETS:
		get_tweets(target)

	driver.quit()

if __name__ == '__main__':
	main()
