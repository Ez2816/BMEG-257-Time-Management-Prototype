# input: string which is the path to the file containing the category 
# and minutes data from the backend

# Output: a dictionary containing the category string as the key and the total minutes integer
# the user spent on the category that week sorted in descending order of minutes spent
 
#If the file is empty or the file does not exist, the function will throw a FileNotFoundError
#If the file is empty, an empty dictionary will be returned


# This function reads the backend ouput file then outputs a dictionary of the total number of 
# minutes per each category. This function serves as the basis of data accumulation for analysis
# from the direct activities of the user wristband and app

# Author: GitHub Copilot and Elsa Zheng

# Note: the parse currently requires a regex of " " and requires categories to be one word
# The location of the regex is marked below for any changes in file formatting



def parseFileToDictionary (filePath: str) -> dict[str, int]:
    #Initializing empty dictionary to store category and minutes data
    categoryMinutes = {}

    try:
        with open(filePath, 'r') as file:

            for line in file:
                #Reading each line and taking away the white space 
                text = line.strip()

                if not text:
                    continue

                #Current regex is assumed to be " " and the category is one word
                category, minutes = text.split()
                minutes = int(minutes)
                
                #Defaulting or updating the dictionary with the category
                categoryMinutes[category] = categoryMinutes.get(category, 0) + minutes

            # Sorting dictionary by minutes in descending order  
            categoryMinutes = dict(sorted(categoryMinutes.items(), key=lambda x: x[1], reverse=True))

    except (FileNotFoundError, ValueError):
        # Throwing Exception if file not found
        raise FileNotFoundError("File not found or invalid file format")
        

    return categoryMinutes
