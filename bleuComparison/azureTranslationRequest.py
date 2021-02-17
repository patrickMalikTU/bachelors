import ast

import requests

if __name__ == '__main__':
    with open("original/5-star.txt", "r", encoding="utf-8") as readFile:
        with open("original/translations/5-star_translated.txt", "w", encoding="utf-8") as testFile:
            lines = readFile.readlines()
            length = len(lines)

            for i in range(0, len(lines)):
                text = lines[i]
                url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
                param = "&to=en"
                region = "westeurope"
                key = "---key---"
                header = {"Content-Type": "application/json",
                          "Ocp-Apim-Subscription-Key": key,
                          "Ocp-Apim-Subscription-Region": region}
                body = [{"text": text}]

                response = requests.post(url + param, json=body, headers=header)

                # ast.literal_eval(response.text)[0].get('translations')[0].get("text"))
                testFile.writelines([response.text])
