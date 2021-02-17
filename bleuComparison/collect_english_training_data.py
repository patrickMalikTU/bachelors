import csv

if __name__ == '__main__':
    collectedReviews = [[], [], [], []]
    review_limit = 2500
    for i in range(0, 1026):
        with open("../csvs/booksDataFiltered_" + str(i) + ".csv") as readFile:
            csvReader = csv.reader(readFile)
            for line in csvReader:
                if line[1] == str(1.0) and len(collectedReviews[0]) < review_limit:
                    collectedReviews[0].append(str(line))  # line[2] would work but would make it hard to deal with \n
                if line[1] == str(2.0) and len(collectedReviews[1]) < review_limit:
                    collectedReviews[1].append(str(line))
                if line[1] == str(4.0) and len(collectedReviews[2]) < review_limit:
                    collectedReviews[2].append(str(line))
                if line[1] == str(5.0) and len(collectedReviews[3]) < review_limit:
                    collectedReviews[3].append(str(line))
        if len(collectedReviews[0]) == review_limit and \
                len(collectedReviews[1]) == review_limit and \
                len(collectedReviews[2]) == review_limit and \
                len(collectedReviews[3]) == review_limit:
            break

    #    print(collectedReviews[0][0][15:-2])
    for review_ind in range(0, len(collectedReviews)):
        lines_to_write = []
        for line in collectedReviews[review_ind]:
            line_split = str(line[15:-2])
            line_split = line_split.replace("\\n", " ")
            line_split = line_split.replace("\\'", "'")
            line_split = line_split.strip()
            lines_to_write.append(line_split + "\n")

        num = review_ind + 1 if review_ind + 1 < 3 else review_ind + 2
        with open("originally_english/" + str(num) + "_star_reviews_orig_english", "w", encoding="utf-8") as writeFile:
            writeFile.writelines(lines_to_write)

