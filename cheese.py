from pandas.io.html import read_html
import pandas as pd
from collections import Counter

# Sample some wiki cheese pages
pages = ["https://en.wikipedia.org/wiki/Brie",
         "https://en.wikipedia.org/wiki/Neufch%C3%A2tel_cheese",
         "https://en.wikipedia.org/wiki/Reblochon",
         "https://en.wikipedia.org/wiki/Sainte-Maure_de_Touraine",
         "https://en.wikipedia.org/wiki/Isle_of_Mull_Cheddar",
         "https://en.wikipedia.org/wiki/Camembert"]

infoboxes = dict()
for page in pages:
    try:
        print(f"Reading page: {page}")
        infobox = read_html(page, attrs={"class": "infobox"})[0]
    except Exception as e:
        if "No tables found" in str(e):
            print(f"Warning: No infobox table found!!")
            continue
        else:
            raise

    # The name of the cheese is the name of the first column
    name = infobox.columns[0]

    # Now rename the columns
    infobox.columns = ['field', 'value']

    # Save it for later inspection
    infoboxes[name] = infobox

# First inspect all the fields found
fields_seen = Counter()
for _, infobox in infoboxes.items():
    fields = infobox['field'].to_list()
    for field in fields:
        fields_seen[field] += 1

print()
print('Fields seen (with occurrence)')
for field, count in fields_seen.items():
    print(f'{field}: {count}')

# Manually inspect the result, and keep only fields we need
fields_needed = [
    'Country of origin',
    'Region, town',
    'Source of milk',
    'Pasteurized',
    'Texture',
    'Aging time',
    'Certification',
    'Named after',
    'Region',
    'Pasteurised',
    'Fat content',
    'Weight'
]

infoboxes_wide = []
for name, infobox in infoboxes.items():
    # Keep only the ones we're interested in.
    infobox2 = infobox[infobox['field'].isin(fields_needed)]

    # Standardize the name of field "Region"
    infobox2.loc[infobox2.field.str.contains(r'Region'), 'field'] = 'Region'
    # Add the name of the cheese as a new column, so that we can pivot on that.
    infobox2['Name'] = name

    # Pivot to make it wide
    # See: https://www.datasciencemadesimple.com/reshape-long-wide-pandas-python-pivot-function/
    infobox_wide = infobox2.pivot(index='Name', columns='field', values='value').reset_index()
    infoboxes_wide.append(infobox_wide)

# Concatenat all the wide infoboxes into a single dataframe, and export it
result = pd.concat(infoboxes_wide, sort='Name')
result.to_csv("result.csv", index=False)