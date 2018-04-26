# Apartments.com Price Scraper

Apartments.com is a website that lists availability and pricing information for apartment buildings all across the country. It's an easy way to compare buildings run by different companies and owners. I wrote this script to take a list of links for building, scrape the HTML, find the lowest price for each floorplan, and append the results to a CSV file. In my own personal setup, I created a cron job to run the script each night (early in the morning) and then setup a separate spreadsheet where I copy and paste the data to for more detailed filtering and analysis.


## Prerequisites

My set up for this script consisted of a Raspberry Pi 3 Model B running the latest version of Raspbian. I haven't tested this on other platforms. The script is written in Python 3. You'll need several third-party Python libraries to support some of the functions in the script. If you don't already have python3-pip installed go ahead and install it with:

```
apt-get install python3-pip
```

Afterwards install BeautifulSoup and requests by running:

```
pip install bs4
pip install requests
```

## Installing / Usage

Once you have the prerequsites installed you should be able to run the script from a terminal using ./apartments.py. The script can be run on an ad-hoc basis with no schedule or you can set up a cron job or similar to automatically run the script. The script is setup to check the CSV for entries from the current date. If there are already entries for today's date then the script will still run but will not modify the CSV file. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


## Future

I haven't looked at this script in some time but there are several ways I've considering enhancing it. First, I would move the list of URLs to a more easily editable location. Currently they're stored hardcoded in an array at the beginning of the script. I also have had thoughts of moving the data storage to an actual database instead of a CSV. For now, I've opted not to as using Excel to analyze is a quick and dirty way that's already vetted. I've also considered the possibiltiy of some sort of web based frontend. I haven't explored much with Flask or Django, I have to imagine it wouldn't be too hard to make a few useful filters, graphs etc.
