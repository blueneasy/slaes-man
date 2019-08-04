from MoreleScraper import Scraper
from Analyser import Analyser

# create a filename with date
current_file = Scraper.file_name()

print(current_file)

# scrap from morele
scrap = Scraper()
scrap.morele_scraper()

# analyse the data
perform = Analyser()
perform.analyse(current_file)



