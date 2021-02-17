import csv

if __name__ == '__main__':
    with open("kindleDatafiltered.csv", "r", encoding="utf-8") as readFile:
        with open("../kindelDataFilteredWithoutEnglish.csv", "w", encoding="utf-8", newline="") as writeFile:
            csvReader = csv.reader(readFile)
            csvWriter = csv.writer(writeFile)
            for line in csvReader:
                if line[0] == "en":
                    continue
                print(line)
                csvWriter.writerow(line)
