import pandas as pd
import json
import re

def convert_to_df(data):
    """
    Convert result to DataFrame structure
    """
    d = {}
    try:
        for menuName, cat in data.items():
            for catName, catInfo in cat.items():
                dProducts = {}
                length = len(catInfo['products'])
                for i in range(10):
                    title = catInfo['products'][i][0] if i < length else None
                    price = catInfo['products'][i][1] if i < length else None
                    dProducts['product_'+str(i+1)] = title
                    dProducts['price_'+str(i+1)] = price
                dProducts['url'] = catInfo['url']
                d[(menuName, catName)] = dProducts
        df = pd.DataFrame.from_dict(d, orient='index')
    except Exception as e:
        print('Invalid result.')
        print('{}: {}'.format(type(e), str(e)))
        print('.\n.\n.')
    return df

def to_json(data, directory, filename):
    """
    Export result to a .json file
    """
    if not filename:
        filename = 'default'
    if not filename.endswith('.json'):
        filename += '.json'

    path = directory + filename
    try:
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        print('{} is saved successfully'.format(filename))
    except Exception as e:
        print('{} : {}'.format(type(e), str(e)))

def to_csv(data, directory, filename):
    """
    Export result to a .csv file
    """
    if not filename:
        filename = 'default'
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    path = directory + filename
    try:
        df = convert_to_df(data)
        df.to_csv(path, encoding='utf_8_sig')
        print('{} is saved successfully'.format(filename))
    except Exception as e:
        print('{} : {}'.format(type(e), str(e)))

def to_excel(data, directory, filename):
    """
    Export result to a .xlsx file
    """
    if not filename:
        filename = 'default'
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    path = directory + filename
    try:
        df = convert_to_df(data)

        # replace the illegal character
        ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
        df = df.applymap(lambda x: ILLEGAL_CHARACTERS_RE.sub(r'', x) if isinstance(x, str) else x)
        
        df.to_excel(path, encoding='utf_8_sig')
        print('{} is saved successfully'.format(filename))
    except Exception as e:
        print('{}: {}'.format(type(e), str(e)))