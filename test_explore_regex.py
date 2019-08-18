from explore_regex import ExploreRegex

import pandas as pd
import re

#Function to see an output from the explore_pattern method
def test_explore_pattern():
    # download data
    path2data = 'https://raw.githubusercontent.com/snorreralund/scraping_seminar/master/english_review_sample.csv'
    df = pd.read_csv(path2data)

    sample_string = '\n'.join(df.sample(1000).reviewBody)
    explore = ExploreRegex(sample_string)

    somepattern = r'(\w+\s){3}'
    explore.explore_pattern(somepattern, n_samples = 30, context=50)

if __name__ == "__main__":
    test_explore_pattern()