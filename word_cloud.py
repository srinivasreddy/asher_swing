#!/usr/bin/env python3

import xlrd
from wordcloud import WordCloud, STOPWORDS
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
from IPython.display import Image as im
from collections import Counter
import re

def _clean_data(raw_string):
    no_links = re.sub(r'http\S+', '', raw_string)
    no_unicode = re.sub(r"\\[a-z][a-z]?[0-9]+", '', no_links)
    no_special_characters = re.sub('[^A-Za-z ]+', '', no_unicode)
    return no_special_characters

def _generate_word_counter(sheet):
    nrows = sheet.nrows
    temp_counter = Counter()
    for row in range(2, nrows):
        _count = sheet.cell(row, 1).value
        clean_data = _clean_data(sheet.cell(row, 4).value)
        temp_counter.update({word.lower():_count  for word in clean_data.split() if word not in STOPWORDS})
    return temp_counter

def generate_word_cloud():
    wb = xlrd.open_workbook("video_activity_metrics_Reuters_20200121_20200127_en.xlsx")
    india_sheet = wb.sheet_by_name('India')
    latin_america_sheet = wb.sheet_by_name('Latam')
    reuters_sheet = wb.sheet_by_name('Reuters')
    business_sheet = wb.sheet_by_name('Biz')
    japan_sheet = wb.sheet_by_name('Japan')
    india_dict = _generate_word_counter(india_sheet)
    import pdb; pdb.set_trace()


if __name__ == "__main__":
    generate_word_cloud()


