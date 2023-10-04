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
import sys
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
import csv_io as cio
import utility as util
#)


def get_webpage(target_url, user_agents):
	headers = {"User-Agent":user_agents[random.randint(0,len(user_agents)-1)] \
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

def get_product_info(asin: str, sleep_duration: float):
	product_info = {}
	specs_arr=[]
	specs_obj={}

	status_code, webpage_response = get_amazon_product_page(asin)
	#print(webpage_response.text)
	print(f"Response status code: {status_code} ; ASIN: {asin}")

	if(status_code != 200):
		print(webpage_response)
	#

	soup=BeautifulSoup(webpage_response.text,'html.parser')

	time.sleep(sleep_duration)

	product_info["date-time"] = util.get_now_str()
	try:
		product_info["title"]=soup.find('h1',{'id':'title'}).text.lstrip().rstrip()
	#
	except:
		product_info["title"]=None
	#
	images = re.findall('"hiRes":"(.+?)"', webpage_response.text)
	product_info["images"]=images

	try:
		product_info["price"]=soup.find("span",{"class":"a-price"}).find("span").text
	#
	except:
		product_info["price"]=None
	#
	
	# TODO(Armağan): Find price from price list.
	if product_info["price"] is None: # If price is not available.
		try:
			#price_text = soup.find("li",{"class":"swatchElement selected"}).find("span", {"class": "a-color-base"}).text
			price_text = soup.find("li",{"class":"swatchElement selected"}).find("span", {"class": "a-button-inner"}).text
			price_text = price_text.strip()
			idx = price_text.find("from")
			
			product_info["price"] = price_text[idx+4:].strip()
		except:
			product_info["price"]=None
	
	
	try:
		product_info["rating"]=soup.find("i",{"class":"a-icon-star"}).text
	#
	except:
		product_info["rating"]=None
	#
	try:
		product_info["rating_count"]=soup.find("span",{'id':'acrCustomerReviewText'}).text
	#
	except:
		product_info["rating_count"]=None
	#
	specs = soup.find_all("tr",{"class":"a-spacing-small"})

	for u in range(0,len(specs)):
		spanTags = specs[u].find_all("span")
		specs_obj[spanTags[0].text]=spanTags[1].text
	#
	
	specs_arr.append(specs_obj)
	product_info["specs"]=specs_arr
	
	return product_info
#

def write_csv_ver_1(file_path, product_infos, **kwargs):
		CSV_VERSION = 1
		
		CSV_DELIMITER = kwargs.get("delimiter", ',')
		CSV_QUOTECHAR = kwargs.get("quotechar", '"')
		
		CSV_INFO_ROW_TYPE = "T:0"
		CSV_PRODUCT_INFO_ROW_TYPE = "T:1"
		
		rows = [
				[CSV_INFO_ROW_TYPE, "==", "Info row"] \
				, [CSV_PRODUCT_INFO_ROW_TYPE, "==", "Date", "Rating count", "Rating", "Price", "Title", "Specs", "Images"] \
				, [CSV_INFO_ROW_TYPE, f"Delimiter: {CSV_DELIMITER}"] \
				, [CSV_INFO_ROW_TYPE, f"QUOTECHAR: {CSV_QUOTECHAR}"] \
		]
			
		for p in product_infos:
			
			row = [CSV_PRODUCT_INFO_ROW_TYPE, p["date-time"], p["rating_count"] \
					, p["rating"], p["price"], p["title"], p["specs"], p["images"]
			]
			
			rows.append(row)	
		#
		cio.csv_write_file(file_path, rows, delimiter = CSV_DELIMITER)
#

def get_product_datas(asin_values: Iterable):
	SLEEP_DURATION_SECONDS = 0.250 # Sleep to avoid IP ban.
	
	product_infos = []

	for asin in asin_values:
		product_info = get_product_info(asin, SLEEP_DURATION_SECONDS)

		product_infos.append(product_info)
	#
	return product_infos
#

def get_asins_from_csv(file_path, **kwargs):
	CSV_DELIMITER = kwargs.get("delimiter", ',')
	
	rows = cio.csv_read_file(file_path, delimiter = CSV_DELIMITER)
	# rows example: [['1982171456'], ['014026468X'], ['B0C7686169'], ['B0BSHF7WHW']]
	
	# Each row should have 1 element (asin).
	for row in rows:
		if len(row) < 1:
			continue
		#
		first_element = row[0]
		
		yield first_element
	#
#

def main(args):
	NOW_STR = util.get_now_str()
	
	fpath = f"amazon_products_({NOW_STR}).csv"
	
	print("[ INFO ] Getting product pages...")
	product_infos = get_product_datas(args["asin_values"])
	
	write_csv_ver_1(fpath, product_infos, delimiter = ';')
	
	print(f"Product data was written to ({fpath})")
#

if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise Exception("Wrong argument count. Provide a .csv that holds an asin code on each line.")
	#
	asins = list(get_asins_from_csv(sys.argv[1], delimiter = ';'))
	
	args = {"asin_values": asins}
	
	main(args)
#
