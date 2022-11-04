import json, csv
import pandas as pd
csvFile = 'data/202111-202207.csv'
# jsonFile = 'data/data.json'

# data = {}

# with open(csvFile, 'r', encoding='utf-8') as csvFile:
#     csvReader = csv.DictReader(csvFile)
#     column_names = csvReader.fieldnames
#     for row in csvReader:
#         # if row[column_names[0]] in data:
#         #     data[row[column_names[0]]].append(row)
#         # else:
#         #     data[row[column_names[0]]] = [row]
#         if row['床位'] not in data:
#             data[row['床位']] = row
        

# with open(jsonFile, 'w', encoding='utf-8') as jsonFile:
#     jsonFile.write(json.dumps(data, indent=4, ensure_ascii=False))

df = pd.read_csv(csvFile)
print(len(df['ID'].unique()))