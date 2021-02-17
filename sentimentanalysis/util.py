from datetime import datetime

from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score


def time_log(message):
    print(datetime.now().strftime("%H:%M:%S ") + message)

class RunConfiguration:
    def __init__(self, run_name, implementation):
        self.run_name = run_name  # "german", "english"
        self.implementation = implementation  # "nb", "svm"

    def print(self):
        print("run_name: " + str(self.run_name))
        print("implementation: " + str(self.implementation))

    @staticmethod
    def generate_run_configs(language_dict_keys):
        # ["svm", "nb", "polyglot", "textblob", "vader", "nlp"]
        implementations = ["vader"]

        # generate all combinations
        return [RunConfiguration(w, x) for w in language_dict_keys for x in implementations]


class F1Composite:
    def __init__(self, ground_truth, predicted_values):
        self.precision = precision_score(ground_truth, predicted_values)
        self.recall = recall_score(ground_truth, predicted_values)
        self.f1 = f1_score(ground_truth, predicted_values)
        self.accuracy = accuracy_score(ground_truth, predicted_values)


