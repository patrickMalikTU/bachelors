import util
from randomizeFromFiles import CompositeFileReader
from standard_run import RunData
from util import RunConfiguration, F1Composite

if __name__ == '__main__':
    util.time_log("starting...")

    filenames_originally_english = ["../reviews/originally_english/1_star_reviews_orig_english.txt",
                                    "../reviews/originally_english/2_star_reviews_orig_english.txt",
                                    "../reviews/originally_english/4_star_reviews_orig_english.txt",
                                    "../reviews/originally_english/5_star_reviews_orig_english.txt"]
    filenames_english_uncorrected = ["../reviews/original/1-star_translated_mapped.txt",
                                     "../reviews/original/2-star_translated_mapped.txt",
                                     "../reviews/original/4-star_translated_mapped.txt",
                                     "../reviews/original/5-star_translated_mapped.txt"]

    k = 20  # 20 so we get 200 per test_set

    run_data_dict = {"english_uncorrected": filenames_english_uncorrected,
                     "originally_english": filenames_originally_english}
    languages_dict = {"english_uncorrected": "english",
                      "originally_english": "english"}

    comp_list = [{"english_uncorrected": 4, "english": 4, "originally_english": 4, "original_german": 4}]

    run_configurations = RunConfiguration.generate_run_configs(run_data_dict.keys())
    run_configs_f1_composite = {x: [] for x in run_configurations}

    run_data = RunData(run_data_dict, k, languages=languages_dict)

    for run_configuration in run_configurations:
        prediction = []
        if run_configuration.implementation == "svm":
            prediction = run_data.run_svm(run_configuration.run_name)
        elif run_configuration.implementation == "nb":
            prediction = run_data.run_naive_bayes(run_configuration.run_name)
        elif run_configuration.implementation == "polyglot":
            prediction = run_data.run_polyglot(run_configuration.run_name)
        elif run_configuration.implementation == "textblob":
            prediction = run_data.run_textblob(run_configuration.run_name)
        elif run_configuration.implementation == "vader":
            prediction = run_data.run_vader(run_configuration.run_name)
        elif run_configuration.implementation == "nlp":
            prediction = run_data.run_nlp(run_configuration.run_name)

        f1_composite_list = []

        for k_iter in range(0, k):
            f1_composite_list.append(
                F1Composite(run_data.test_data_rating(run_configuration.run_name, k_iter), prediction[k_iter]))

        run_configs_f1_composite[run_configuration] = f1_composite_list

    for key in run_configs_f1_composite.keys():
        f1_composite_lists_list = run_configs_f1_composite[key]
        f1_list = [x.f1 for x in f1_composite_lists_list]
        prec_list = [x.precision for x in f1_composite_lists_list]
        rec_list = [x.recall for x in f1_composite_lists_list]
        acc_list = [x.accuracy for x in f1_composite_lists_list]

        key.print()
        print("f1-average: " + str(sum(f1_list) / k))
        print("precision-average: " + str(sum(prec_list) / k))
        print("recall-average: " + str(sum(rec_list) / k))
        print("accuracy-average: " + str(sum(acc_list) / k))

        print("f1-median: " + str(median(f1_list)))
        print("precision-median: " + str(median(prec_list)))
        print("recall-median: " + str(median(rec_list)))
        print("accuracy-median: " + str(median(acc_list)))

        print("f1-min: " + str(min(f1_list)))
        print("precision-min: " + str(min(prec_list)))
        print("recall-min: " + str(min(rec_list)))
        print("accuracy-min: " + str(min(acc_list)))

        print("f1-max: " + str(max(f1_list)))
        print("precision-max: " + str(max(prec_list)))
        print("recall-max: " + str(max(rec_list)))
        print("accuracy-max: " + str(max(acc_list)))

        print("#######################################################")
