#!/usr/bin/env python3

import xlrd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import re
import MeCab
import ftfy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

ES_STOPWORDS = set(stopwords.words('spanish'))




def _clean_data(raw_string):
    no_links = re.sub(r"http\S+", "", raw_string)
    # no_unicode = re.sub(r"\\[a-z][a-z]?[0-9]+", "", no_links)
    # no_special_characters = re.sub("[^A-Za-z ]+", "", no_unicode)
    # return no_special_characters
    return no_links


JP_STOP_WORDS = {
    "てる",
    "いる",
    "なる",
    "れる",
    "する",
    "ある",
    "こと",
    "これ",
    "さん",
    "して",
    "くれる",
    "やる",
    "くださる",
    "そう",
    "せる",
    "した",
    "思う",
    "それ",
    "ここ",
    "ちゃん",
    "くん",
    "",
    "て",
    "に",
    "を",
    "は",
    "の",
    "が",
    "と",
    "た",
    "し",
    "で",
    "ない",
    "も",
    "な",
    "い",
    "か",
    "ので",
    "よう",
    "",
    "れ",
    "さ",
    "なっ",
}


def mecab_analysis(sheet):
    nrows = sheet.nrows
    word_counter = Counter()
    for row in range(2, nrows):
        text = sheet.cell(row, 4).value
        _count = sheet.cell(row, 1).value
        t = MeCab.Tagger("-Ochasen")
        t.parse("")
        text = re.sub(r"http\S+", "", text)
        node = t.parseToNode(text)
        output = []
        while node:
            if node.surface != "":
                word_type = node.feature.split(",")[0]
                if word_type in ["形容詞", "動詞", "名詞", "副詞"]:
                    if node.surface not in JP_STOP_WORDS:
                        output.append(node.surface)
            node = node.next
            if node is None:
                break
        word_counter.update({word: _count for word in output})
    return word_counter


def spanish_analysis(sheet):
    nrows = sheet.nrows
    word_counter = Counter()
    for row in range(2, nrows):
        text = sheet.cell(row, 4).value
        _count = sheet.cell(row, 1).value
        text = re.sub(r"http\S+", "", text)
        output = [esp_token for esp_token in word_tokenize(text)]
        word_counter.update({word: _count for word in output if word not in ES_STOPWORDS})
    return word_counter


def _generate_word_counter(sheet):
    nrows = sheet.nrows
    word_counter = Counter()
    for row in range(2, nrows):
        _count = sheet.cell(row, 1).value
        clean_data = _clean_data(sheet.cell(row, 4).value)
        word_counter.update({word.lower(): _count for word in clean_data.split() if word.lower() not in STOPWORDS})
    return word_counter


def generate_word_cloud(freq_counter, file_name, **kwargs):
    wordcloud = WordCloud(max_words=100, background_color="white", **kwargs).fit_words(
        freq_counter
    )
    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.draw()
    plt.savefig(file_name + ".png", dpi=200)


def _main():
    wb = xlrd.open_workbook("video_activity_metrics_Reuters_20200121_20200127_en.xlsx")
    india_sheet = wb.sheet_by_name("India")
    latin_america_sheet = wb.sheet_by_name("Latam")
    reuters_sheet = wb.sheet_by_name("Reuters")
    business_sheet = wb.sheet_by_name("Biz")
    japan_sheet = wb.sheet_by_name("Japan")
    india_dict = _generate_word_counter(india_sheet)
    generate_word_cloud(india_dict, "India")
    business_dict = _generate_word_counter(business_sheet)
    generate_word_cloud(business_dict, "Biz")
    reuters_dict = _generate_word_counter(reuters_sheet)
    generate_word_cloud(reuters_dict, "Reuters")
    latin_america_dict = spanish_analysis(latin_america_sheet)
    generate_word_cloud(latin_america_dict, "Latam")
    japan_dict = mecab_analysis(japan_sheet)
    generate_word_cloud(
        japan_dict,
        "Japan",
        stopwords=JP_STOP_WORDS,
        font_path="/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
    )


if __name__ == "__main__":
    _main()
