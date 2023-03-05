import ui
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlparse, urlsplit
from collections import deque
import re
import sys
import clipboard

datasource = ui.ListDataSource(range(20))
datasource.items = []
RUN = True

def kill_process(sender):
	global RUN
	label = sender.superview['lab2']
	label.text = f"process killed"
	RUN = False
	


	
def clipit(sender):
	label = sender.superview['lab2']
	row = datasource.selected_row
	clipboard.set(datasource.items[row])
	label.text = f"{datasource.items[row]} clipped!"
	

	
@ui.in_background
def email_scrapper(sender):
	global RUN
	url = sender.superview['url'].text
	label = sender.superview['lab2']
	label.text = f"[+] scan de l'url : {url}"
	
	count = 0
	user_url = url
	urls = deque([user_url])
	urls_scraped = set()
	emails = set()
	
	try:
		while len(urls):
			if not RUN:
				break
				
			count += 1
			if count == 100:
				label.text = 'done'
				break
			url = urls.popleft()
			urls_scraped.add(url)
	
			parties = urlsplit(url)
			url_de_base = '{0.scheme}://{0.netloc}'.format(parties)
	
			path = url[:url.rfind('/') + 1] if '/' in parties.path else url
	
			label.text = f"[{count}] processing : {url}"
			try:
				response = requests.get(url)
			except (requests.exceptions.MissingSchema,requests.exceptions.ConnectionError):
				label.text = f"error"
	
			nouveaux_emails = set(
				re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
			emails.update(nouveaux_emails)
	
			soup = BeautifulSoup(response.text,
			"html.parser")
	
			for anchor in soup.find_all("a"):
				lien = anchor.attrs['href'] if 'href' in anchor.attrs else  ''
				
				if lien.startswith('/'):
					lien = url_de_base + lien
				elif not lien.startswith(urlparse(url_de_base).scheme):
					lien = path + lien
				if urlparse(lien).netloc != urlparse(url_de_base).netloc:
					label.text = 'inccorect link'
					lien = ''
				else:
					if not lien in urls and not lien in urls_scraped:
						urls.append(lien)
	except KeyboardInterrupt:
		label.text = f"[-] Fermeture!"
	
	for mail in list(emails):
		datasource.items.append(mail)


v = ui.load_view()
v.get_key_commands()
tv = v['table']
tv.data_source = tv.delegate = datasource


v.present('sheet')


