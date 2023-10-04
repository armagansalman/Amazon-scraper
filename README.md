# Amazon-scraper
## Usage
Warning: Make sure you use time.sleep between retrievals to avoid IP ban.
<br><br>Put Amazon ASIN codes (the code after dp/ in the URL of the product) in asin_data.csv on each line.
Go to src directory in terminal. Then:
<br><br>For Linux:
<br>python3 amazon_scraper.py asin_data.csv
<br><br>For Windows:
<br>py amazon_scraper.py asin_data.csv

Results will be in a .csv file which contains the script's starting time.
