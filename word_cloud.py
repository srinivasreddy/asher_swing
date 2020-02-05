#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import re
import MeCab
import ftfy
import mysql.connector
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

ES_STOPWORDS = set(stopwords.words("spanish"))


def connection_from_mysql():
    db_connection = mysql.connector.connect(
        host="localhost", user="root", passwd="root@1434", database="test",
    )
    return db_connection


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


def generate_japanese_word_counter(japanese_table_name):
    sql_statement = "SELECT views, text_data FROM {};".format(japanese_table_name)
    word_counter = Counter()
    connection = connection_from_mysql()
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    for row in cursor:
        text = row[1]
        _count = int(row[0])
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
    connection.close()
    return word_counter


def generate_spanish_word_counter(spanish_table_name):
    sql_statement = "SELECT views, text_data FROM {};".format(spanish_table_name)
    word_counter = Counter()
    connection = connection_from_mysql()
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    for row in cursor:
        text = row[1]
        _count = int(row[0])
        text = re.sub(r"http\S+", "", text)
        output = [esp_token for esp_token in word_tokenize(text)]
        word_counter.update(
            {word: _count for word in output if word not in ES_STOPWORDS}
        )
    connection.close()
    return word_counter


def generate_word_counter(table_name):
    sql_statement = "SELECT views, text_data FROM {};".format(table_name)
    word_counter = Counter()
    connection = connection_from_mysql()
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    for row in cursor:
        _count = int(row[0])
        clean_data = _clean_data(row[1])
        word_counter.update(
            {
                word.lower(): _count
                for word in clean_data.split()
                if word.lower() not in STOPWORDS
            }
        )
    connection.close()
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
    india_dict = generate_word_counter("test.word_cloud")
    generate_word_cloud(india_dict, "India")
    business_dict = generate_word_counter("Business_tweets_table_name")
    generate_word_cloud(business_dict, "Biz")
    reuters_dict = generate_word_counter("Reuters_tweets_table_name")
    generate_word_cloud(reuters_dict, "Reuters")
    latin_america_dict = generate_spanish_word_counter("Latam_tweets_table_name")
    generate_word_cloud(latin_america_dict, "Latam")
    japan_dict = generate_japanese_word_counter("Japanese_tweets_table_name")
    generate_word_cloud(
        japan_dict,
        "Japan",
        stopwords=JP_STOP_WORDS,
        font_path="/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
        # This may not work on your system unless it is a macos,
        # so you have to install japanese fonts on your system to display japanese characters properly.
        # Please see this article on how to install japanese fonts.
        # http://about-t3ch.blogspot.com/2015/04/how-to-install-japanese-font-in-linux.html
        # Or
        # Download it from here - https://github.com/posteroffonts/sanfran/blob/master/System/Library/Fonts/%E3%83%92%E3%83%A9%E3%82%AE%E3%83%8E%E4%B8%B8%E3%82%B4%20ProN%20W4.ttc
    )


if __name__ == "__main__":
    _main()
