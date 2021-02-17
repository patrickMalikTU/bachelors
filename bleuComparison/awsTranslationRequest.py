import boto3

if __name__ == '__main__':
    translate = boto3.client(service_name='translate',
                             region_name='eu-central-1',
                             )

    with open("deutsch.txt", "r", encoding="utf-8") as readFile:
        with open("aws.txt", "w", encoding="utf-8") as writeFile:
            transLines = readFile.readlines()
            for line in transLines:
                response = translate.translate_text(
                    Text=line,
                    SourceLanguageCode='de',
                    TargetLanguageCode='en'
                )
                print(response)
                writeFile.write(response["TranslatedText"])
