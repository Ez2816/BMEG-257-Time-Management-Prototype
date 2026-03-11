# input: string which is the path to the file containing the category 
# and minutes data from the backend
# Output: a dictionary containing the category string as the key and the total minutes integer
# the user spent on the category that week sorted in descending order of minutes spent
# This function reads the backend ouput file then outputs a dictionary of the total number of 
# minutes per each category. This function serves as the basis of data accumulation for analysis
# from the direct activities of the user wristband and app

# Author: GitHub Copilot and Elsa Zheng

# Note: the parse currently requires a regex of " " and requires categories to be one word
# The location of the regex is marked below for any changes in file formatting



def loadFile (filePath: str) -> dict[str, int]:
    categoryMinutes = {}

    with open(filePath, 'r') as file:

        for line in file:
            input = line.strip()

            if not input:
                continue

            category, minutes = input.split()
            minutes = int(minutes)
            
            categoryMinutes[category] = categoryMinutes.get(category, 0) + minutes
            
        categoryMinutes = dict(sorted(categoryMinutes.items(), key=lambda x: x[1], reverse=True))

    return categoryMinutes
