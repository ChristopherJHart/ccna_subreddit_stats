import requests
import sys
import json
import ast
import time
from statistics import mean, median
import pprint

def get_new_posts_json(after_timestamp=None):
    api_url = "https://www.reddit.com/r/ccna/new.json?limit=100"
    if after_timestamp:
        api_url += "&after={}".format(after_timestamp)
    print("\tAPI URL: {}".format(api_url))
    user_agent = "ccna_stats v0.0.1 by /u/_chrisjhart"
    res = requests.get(api_url, headers = {"User-agent": user_agent})
    try:
        res.raise_for_status()
    except Exception as exc:
        print("Exception encountered when grabbing new posts: {}".format(exc))
        sys.exit()
    return json.loads(res.content)

def write_posts_to_file(post_data_list, filename, writemode):
    with open(filename, writemode) as outfile:
        for post in post_data_list:
            post_dict = {}
            post_dict["author"] = post.get("data").get("author")
            post_dict["time_created"] = post.get("data").get("created")
            post_dict["title"] = post.get("data").get("title")
            post_dict["post_url"] = post.get("data").get("url")
            post_dict["num_comments"] = post.get("data").get("num_comments")
            outfile.write("{}\n".format(post_dict))
    print("\tAll post information written to file")

def analyze_posts(OUT_FILENAME):
    with open(OUT_FILENAME) as datafile:
        post_dict_list = datafile.readlines()
    trigger_words = ["pass", "fail"]
    total_pass_fail_posts = 0
    with open("ccna_pass_fail.txt", "w") as ccnafile:
        unique_authors = set()
        unique_num_comments = []
        for post_line in post_dict_list:
            post = ast.literal_eval(post_line)
            title = post.get("title")
            author = post.get("author")
            unique_authors.add(author)
            for word in trigger_words:
                if word in title.lower():
                    total_pass_fail_posts += 1
                    unique_num_comments.append(post.get("num_comments"))
                    ccnafile.write("{}\n".format(title))
    print("{} matching out of {}".format(total_pass_fail_posts, len(post_dict_list)))
    print("Percentage: {}".format(total_pass_fail_posts/len(post_dict_list)*100))
    print("{} unique authors found.".format(len(unique_authors)))
    print("Comments stats | Min: {} Max: {} Mean: {} Median: {}".format(min(unique_num_comments), max(unique_num_comments), mean(unique_num_comments), median(unique_num_comments)))

        

OUT_FILENAME = "ccna_stats_outfile.txt"
ANALYSIS_MODE = False

if ANALYSIS_MODE:
    print("Analysis mode active, not grabbing new posts. Analyzing existing data.")
    analyze_posts(OUT_FILENAME)
else:
    print("Analysis mode not active, grabbing new posts")
    print("First 100 posts...")
    new_posts_json = get_new_posts_json()
    after = new_posts_json.get("data").get("after")
    post_data_list = new_posts_json.get("data").get("children")
    write_posts_to_file(post_data_list, OUT_FILENAME, "w")
    for i in range(1, 10):
        time.sleep(1)
        print("Next iteration {}".format(i))
        new_posts_json = get_new_posts_json(after)
        after = new_posts_json.get("data").get("after")
        post_data_list = new_posts_json.get("data").get("children")
        write_posts_to_file(post_data_list, OUT_FILENAME, "a")
    analyze_posts(OUT_FILENAME)