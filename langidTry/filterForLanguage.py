import csv

if __name__ == '__main__':
    language = "de"
    with open("kindleDatafilteredAgain.csv", "r", encoding="utf-8") as readFile:
        with open("kindleDataFilteredAgain_" + language + ".csv", "w", encoding="utf8", newline="") as writeFile:
            csvReader = csv.reader(readFile)
            csvWriter = csv.writer(writeFile)
            for row in csvReader:
                if row[0] == language:
                    csvWriter.writerow([row[1], row[2]])
