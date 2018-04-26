#!/usr/bin/python3
'''
MIT License

Copyright (c) 2018 Jon Anderson

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


This program accepts a list of URLs (each property's specific page) and then will
parse the pricing for each floorplan. Results are stored in [csv|database]
'''

# Import libraries
# sudo apt-get install python3-pip
# pip install bs4 -- Run from terminal or command line
# pip install requests -- Run from terminal or command line
from bs4 import BeautifulSoup         	# Used for parsing the DOM
import requests							# Used for loading the pages
import re								# Used for splitting double whitespace
import datetime as dt					# Used for getting today's date
from time import sleep					# Used for waiting
import random							# Used for generating a random number (which we will wait using)
import csv								# Used to read and write from our csv file storing the information
from collections import deque			# Used to read last line from CSV file

# Function from StackOverflow to get last line of CSV file
# https://stackoverflow.com/questions/20296955/attributeerror-when-trying-to-use-seek-to-get-last-row-of-csv-file
def get_last_row(csv_filename):
    with open(csv_filename, 'r') as f:
        try:
            lastrow = deque(csv.reader(f), 1)[0]
        except IndexError:  # empty file
            lastrow = None
        return lastrow

# Get today's date
today = dt.datetime.today().strftime("%m/%d/%y")

# Setup aggreate dictionary for storing availability at each property the script examines
aggregate_dict = {}

# Setup property list
property_list = ["https://www.apartments.com/cityscape-residences-phoenix-az/4zbhsej/, \
				"https://www.apartments.com/broadstone-roosevelt-row-phoenix-az/1jrhhy4/"]

# Alert user that price search has begun
print("Beginning apartment price search...\n")

# Loop through list of properties				
for property in property_list:

	# Open and parse the page to scrape
	scrape_url = property
	response = requests.get(scrape_url)
	soup = BeautifulSoup(response.content, "html.parser")

	# Get property name
	property_name = soup.find('h1', class_='propertyName').text.strip()
	print("Obtaining prices for: " + property_name)
	
	# Get table of availability (each item in table has the class 'rentalGridRow'), this is returned as a list
	availability_table = soup.findAll(class_='rentalGridRow')
	
	# Create empty dictionary to be populated as this sorts through each row
	availability_dict = {}
	
	# Loop through the list of rows in the availability table
	for row in availability_table:
		
		# Split each row into list elements using a regular expression (the regex below seems to handle the giberish (jiberish?) white space the webpage spits out)
		row = re.split('\n[0-9]*\n|\s{2,}', row.text.strip())
		
		# Clean up each list by removing unneeded elements from extracted row
		# Eg. Duplicate data and unused data
		indexes_to_del = [0, 1, 3, 4, 7, 10, 11]
		for i in sorted(indexes_to_del, reverse=True):
			del row[i]

		# Format and organize each row
		# formatted_row = [0 Property Name Floorplan, 1 Floorplan, 2 Rent, 3 Bed/Bath, 4 SqFt]
		formatted_row = []
		formatted_row.append(property_name + " " + row[4])											# 0 Property Name Floorplan
		formatted_row.append(row[4].replace(",",""))												# 1 Floorplan
		if row[2] == 'Call for Rent':																# 2 Rent (ignores non-numbers)
			continue																					# Proceed to next row in availability_table if "Call for Rent"
		formatted_row.append("$" + row[2].split()[0][1:].replace(",",""))								# Remove comma from rent price and append to formatted row
		formatted_row.append(str(row[0].split()[0]) + " BR / " + str(row[1].split()[0]) + " BA")	# 3 Bed/Bath
		formatted_row.append(str(row[3].split()[0].replace(",","")) + " SqFt")						# 4 Square Feet

		# Put the current floorplan into a variable for better code readability
		current_floorplan = formatted_row[0]
		
		# Put the data for the current floorplan into a variable for readability
		# current_floorplan_info = [0 Floorplan, 1 Rent, 2 Bed/Bath, 3 Square Feet]
		current_floorplan_info = formatted_row[1:]
		
		# Check if this floorplan has already been added to the dictionary (availability_table)
		# Stored in the key by floorplan (not prop_floorplan)
		if current_floorplan in availability_dict:
			
			# Store prices in variables for better readability
			# cur_price is in the dictionary
			# new_price is from the row being iterated on now and we're seeing if its lower than whats in the dictionary
			cur_price = availability_dict[current_floorplan][1]
			new_price = formatted_row[2]
			
			# If floorplan exists in the dictionary, check if current row's price (new) is less than what is currently in the dictionary
			if new_price < cur_price:
				availability_dict[current_floorplan] = current_floorplan_info
			
			# Continue to next row in the availability_table if the price is not lower
			else:
				continue
		
		# If the current floorplan isn't in the availability_dict then add it
		else:
			availability_dict[current_floorplan] = current_floorplan_info
	
	# Add the dictionary of availabity for this propety to the aggregate (master) dictionary containing all the properties
	# Each property is stored in the master dictionary using the property name as key and its returned value is the dictionary of availability
	aggregate_dict[property_name] = availability_dict
	
	# Wait 1-3 sec before continuing
	sleep(random.randrange(1,4))
		
# Print a line to separate running lines from output
print()

# Print out each property's information by floorplan
for property in aggregate_dict:
	if aggregate_dict[property]:
		print(property)
	else:
		print("No pricing available at " + property)
	for prop_floorplan in aggregate_dict[property]:
		print(today + ", " + ", ".join(aggregate_dict[property][prop_floorplan]))
	print()

# Print out a nice spacer before moving to the file updating section
print("------------------------------------------------------------")
print()
	
# Append csv data file (if data has not been recorded for today yet)
print("Preparing to update data file with today's pricing")
print()

# Open file using 'with' so that it automatically closes when done
# 'a' is the append option, not using 'ab' since that is for writing direct byte data
# As of Python 3, the CSV writer needs to have the newline option specified to avoid double line spacing
with open('./apartments_data.csv', 'a', newline='') as data_file:
	
	# Create object to append rows to CSV file with
	writer = csv.writer(data_file)
	
	# If file is empty or no data for today then proceed with appending the file
	if (get_last_row('./apartments_data.csv') == None) or not (get_last_row('./apartments_data.csv')[0] == today):
		
		# Append data for each property to the CSV file
		for property in aggregate_dict:
			
			# Plain english on this: if the dictionary key has values associated with it there will be a "True" returned
			if aggregate_dict[property]:
				for prop_floorplan in aggregate_dict[property]:
					temp_row = today + "," + property + "," + ",".join(aggregate_dict[property][prop_floorplan])
					writer.writerow(temp_row.split(","))
		
		# Skip property if there was no pricing data for it (eg. "Call for pricing")
			else:
				continue
	
	# Skip if today's data was already recorded
	else:
		print("Data already entered for today, skipping update of data file")
print()

# Print out a nice spacer before moving to end of the program
print("------------------------------------------------------------")
print()

# Stay running until a key is pressed
# input("Press the <Enter> key on the keyboard to exit.")
