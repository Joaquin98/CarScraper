
import re

string = 'https://www.autotrader.com/cars-for-sale/vehicledetails.xhtml?listingId=692282996&endYear=2022&firstRecord=312&isNewSearch=false&listingTypes=USED&makeCodeList=LAM&marketExtension=include&numRecords=24&referrer=%2Fcars-for-sale%2Flamborghini%3FendYear%3D2022%26firstRecord%3D312%26isNewSearch%3Dfalse%26marketExtension%3Dinclude%26numRecords%3D24%26searchRadius%3D0%26sortBy%3Drelevance%26startYear%3D2010&searchRadius=0&sortBy=relevance&startYear=2010&clickType=listing'

# Three digit number followed by space followed by two digit number
pattern = 'listingId=(\d{9})'

# match variable contains a Match object.
match = re.search(pattern, string)

if match:
    print(match.group(1))
else:
    print("pattern not found")

# Output: 801 35
