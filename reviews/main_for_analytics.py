#!/usr/bin/env python3
import os
import re
from collections import Counter

import nltk
from nltk.corpus import stopwords

from reviews.repository import *
from reviews.uni_list import *

nltk.download("stopwords")

mystem_executable_path = "/opt/mystem/mystem"
tmp_review_file = "/tmp/review.txt"
tmp_review_mystemed_file = "/tmp/review.txt.mystemed"
tmp_all_reviews_file = "/tmp/all_reviews.txt"
russian_stopwords = stopwords.words("russian")
russian_custom_stopwords = ["весь", "это", "очень", "который", "студент", "вуз", "преподаватель", "мочь", "курс",
                            "человек", "университет", "учиться", "факультет"]
stopwords = russian_stopwords + russian_custom_stopwords


def append_file(path, text):
    text_file = open(path, "a")
    text_file.write("\n\n")
    text_file.write(text)
    text_file.close()


def write_file(path, text):
    text_file = open(path, "w")
    text_file.write(text)
    text_file.close()


def read_file(path):
    file = open(path, 'r')
    all_of_it = file.read()
    file.close()
    return all_of_it


def parse_date(date):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    result = datetime.datetime.strptime(date, u'%Y-%m-%d')
    return result


def bag_of_words(reviews):
    try:
        os.remove(tmp_all_reviews_file)
    except Exception:
        pass
    for review in reviews:
        write_file(tmp_review_file, review.text)
        os.system(mystem_executable_path + " " + tmp_review_file + " -l >" + tmp_review_mystemed_file)
        mystemed_text = read_file(tmp_review_mystemed_file)
        mystemed_cleared_text = re.sub(r'{(.+?)}', '\\1 ', mystemed_text)
        mystemed_cleared_text = re.sub(r'[|].*?[ ]', ' ', mystemed_cleared_text)
        mystemed_cleared_text = re.sub(r'[?]', '', mystemed_cleared_text)
        append_file(tmp_all_reviews_file, mystemed_cleared_text)
    data_set = read_file(tmp_all_reviews_file)
    split_it = data_set.split()
    split_it = list(filter(lambda x: x not in stopwords, split_it))
    counter = Counter(split_it)
    most_occur = counter.most_common(20)
    print(most_occur)


if __name__ == '__main__':
    years = range(2013, 2021)
    conn, cursor = init("db.sqlite")

    print("Reviews per year:")
    print("uni|", end='')
    for year in years:
        print(year, "|", sep='', end='')
    print()

    for uni_idx in range(0, len(university_list_tabiturient)):
        reviews = get_for_uni(conn, cursor, uni_idx)
        print(university_list_tabiturient[uni_idx] + "|", end='')
        for year in years:
            date_from = parse_date(str(year) + "-01-01")
            date_to = parse_date(str(year) + "-12-31")
            reviews_f = list(filter(lambda x: date_from <= x.date <= date_to, reviews))
            print(len(reviews_f), "|", sep='', end='')
        print()

    print("\n\nAvg rating per year:")
    print("uni|", end='')
    for year in years:
        print(year, "|", sep='', end='')
    print()

    for uni_idx in range(0, len(university_list_tabiturient)):
        reviews = get_for_uni(conn, cursor, uni_idx)
        print(university_list_tabiturient[uni_idx] + "|", end='')
        for year in years:
            date_from = parse_date(str(year) + "-01-01")
            date_to = parse_date(str(year) + "-12-31")
            reviews_f = list(filter(lambda x: date_from <= x.date <= date_to, reviews))
            marks = list(map(lambda x: x.mark, reviews_f))
            if len(marks) > 0:
                mark_avg = sum(marks) / len(marks)
            else:
                mark_avg = 0
            print(mark_avg, "|", sep='', end='')
        print()

    print("\n")
    for uni_idx in range(0, len(university_list_tabiturient)):
        reviews = get_for_uni(conn, cursor, uni_idx)
        print("Bag of words for uni", university_list_tabiturient[uni_idx])
        bag_of_words(reviews)

    close(conn)
    print("done")