# I've downloaded a dataset of first names from https://github.com/MatthiasWinkelmann/firstname-database and
# added it to a /data folder in this repository.

# Let's load that into memory, and throw out all but the Estonian and German first names.

# load libraries:
# pandas is a nice data science library, very handy here

import pandas as pd


# read the data
firstnames_df = pd.read_csv('data/firstnames.csv', sep=";")

# discard rows that do not have a value in 'Germany' or 'Estonia' -columns
# With this data you might want to
firstnames_df = firstnames_df[~firstnames_df.Germany.isna() | ~firstnames_df.Estonia.isna()]

# only keep columns for name, gender
firstnames_df = firstnames_df[['name', 'gender']]

# Actually, let's make that a dictionary, easier for our purposes later.
# We'll lowercase all the names to make comparison easier.
firstnames_dict = dict()
for index, row in firstnames_df.iterrows():
    firstnames_dict[row['name'].lower()] = row['gender']


# Create a function that is given a name, the list of first names and genders, and that returns a gender
def get_gender_for_firstname(firstname, gender_dict):
    if firstname.lower() in gender_dict.keys():
        return gender_dict[firstname.lower()]
    else:
        return 'not found'


# eg.:
get_gender_for_firstname('Anna', firstnames_dict)

# For OCR errors and non-matching names, you might want to do a test with some kind of partial string comparison
# algorithm. A nice simple one for PYthon is a library called fuzzywuzzy
# https://pypi.org/project/fuzzywuzzy/


from fuzzywuzzy import process


# eg. testing the matching (see the link above for documentation):
choices = list(firstnames_dict.keys())  # Choices for the algorithm to pick from
process.extract(query="Amma", choices=choices, limit=5)
# Testing with a nonsensical word to see where to draw the threshold (or if one can be sensibly set at all):
process.extract(query="Ocrnoise", choices=choices, limit=5)
process.extractOne(query="Amma", choices=choices)


# Modify the simple function above to include a guesser if no exact match is found:
def get_gender_for_firstname_guesser(firstname, gender_dict, threshold=75):
    if firstname.lower() in gender_dict.keys():
        return {'gender': gender_dict[firstname.lower()], 'gender_name_match': 'exact'}
    else:
        choices = list(firstnames_dict.keys())
        guess = process.extractOne(query=firstname, choices=choices)
        # If the match threshold (percentage) is equal or greater than that set in the function parameters,
        # return the result. It's a good idea to show how it was obtained too.
        if guess[1] >= threshold:
            return {'gender': gender_dict[guess[0]], 'gender_name_match': 'fuzzy'}
        # and if the match is below the threshold, don't return a gender:
        else:
            return {'gender': '', 'gender_name_match': 'not found'}


# usage, eg.:
get_gender_for_firstname_guesser('Johan', firstnames_dict, threshold=75)
get_gender_for_firstname_guesser('Amma', firstnames_dict, threshold=75)
get_gender_for_firstname_guesser('Ocrnoise', firstnames_dict, threshold=75)


# and let's apply that to a mock dataset:
testdata = pd.read_csv('data/mockdata.csv')

# add columns for gender and gender match method to the dataset:
testdata['gender'] = ''
testdata['gender_name_match'] = ''

# and then iterate over the data, assigning genders:

for index, row in testdata.iterrows():
    genderdata = get_gender_for_firstname_guesser(row['first_name'], firstnames_dict, threshold=75)
    print(genderdata)
    testdata['gender'][index] = genderdata['gender']
    testdata['gender_name_match'][index] = genderdata['gender_name_match']

# and write the results:
testdata.to_csv('data/testdata_out.csv', index=False)
