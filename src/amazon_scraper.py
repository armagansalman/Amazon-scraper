"""
MIT License

Copyright (c) 2023 Armağan Salman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


# Code inspired from:
# https://www.scrapingdog.com/blog/scrape-amazon/#Changing_Headers_on_every_request

#(
import time
from typing import Iterable
#)

#(
import requests
from bs4 import BeautifulSoup
import re
import random
#)

#( local imports
import user_agents as ua
#)


def get_webpage(target_url, user_agents):
	headers = {"User-Agent":user_agents[random.randint(0,len(user_agents))] \
				,"accept-language": "en-US,en;q=0.9" \
				,"accept-encoding": "gzip, deflate, br" \
				,"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
	#
	resp = requests.get(target_url,headers=headers)
	
	return (resp.status_code, resp)
#

def get_amazon_product_page(asin: str):
	"""
	asin = Amazon Standard Identification Number
	"""
	
	target_url = "https://www.amazon.com/dp/" + asin
	
	user_agents = ua.get_user_agents()
	
	return get_webpage(target_url, user_agents)
#

def get_multiple_amazon_product_pages(multi_asin: Iterable[str]):
	for asin in multi_asin:
		yield get_amazon_product_page(asin)
#

def get_product_info(asin: str):
	product_info = {}
	specs_arr=[]
	specs_obj={}

	status_code, webpage_response = get_amazon_product_page(asin)

	print(f"Response status code: {status_code}")

	if(status_code != 200):
		print(webpage_response)
	#


	soup=BeautifulSoup(webpage_response.text,'html.parser')

	SLEEP_DURATION_SECONDS = 1

	time.sleep(SLEEP_DURATION_SECONDS)

	try:
		product_info["title"]=soup.find('h1',{'id':'title'}).text.lstrip().rstrip()
	except:
		product_info["title"]=None

	"""
	images = re.findall('"hiRes":"(.+?)"', resp.text)
	product_info["images"]=images
	"""

	try:
		product_info["price"]=soup.find("span",{"class":"a-price"}).find("span").text
	except:
		product_info["price"]=None

	if product_info["price"] is None:
		try:
			product_info["price"]=soup.find("span",{"class":"a-color-base"}).find("span").text
		except:
			product_info["price"]=None


	try:
		product_info["rating"]=soup.find("i",{"class":"a-icon-star"}).text
	except:
		product_info["rating"]=None

	try:
		product_info["rating_count"]=soup.find("span",{'id':'acrCustomerReviewText'}).text
	except:
		product_info["rating_count"]=None



	"""
	specs = soup.find_all("tr",{"class":"a-spacing-small"})

	for u in range(0,len(specs)):
		spanTags = specs[u].find_all("span")
		specs_obj[spanTags[0].text]=spanTags[1].text
	"""

	"""
	specs_arr.append(specs_obj)
	product_info["specs"]=specs_arr
	"""
	
	return product_info
#



asin = "B0BSHF7WHW"
asin = "1982171456"



l.append(product_info)

for x in l:
	for k, v in x.items():
		print("~ ", k, " ", v)
