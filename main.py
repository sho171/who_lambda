import os
import MeCab
import neologdn
import tweepy
import pdb
import re
import emoji
import collections
import json
from dotenv import load_dotenv
load_dotenv()


def get_tweet(screen_name):
    # 秘匿情報にする
    consumer_key = os.environ['consumer_key']
    consumer_secret = os.environ['consumer_secret']

    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    limit = api.rate_limit_status()

    # 残りアクセス可能回数が無ければエラー
    if limit['resources']['statuses']['/statuses/user_timeline']['remaining'] == 0:
        return(429)

    # 鍵アカウント処理
    for user in api.lookup_users(screen_name = screen_name):
        protected = user.protected
    if protected:
        return(403)

    tweet_count = 1000
    tweets = [status for status in tweepy.Cursor(api.user_timeline, screen_name = screen_name, count = 200, tweet_mode = 'extended', include_rts = 'false').items(tweet_count)]
    return(tweets)


def tweet_clean(tweet):
    # @ユーザ名除外
    tweet = re.sub('^@.+ ', '', tweet)
    # URL除外
    tweet = re.sub('https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', tweet)
    # 全角 to 半角
    tweet = neologdn.normalize(tweet)
    #emoji除外
    tweet = ''.join(c for c in tweet if c not in emoji.UNICODE_EMOJI['en'])
    tweet = tweet.replace('\u200d', '').replace('\'️️️\'', '')
    #記号除外
    tweet = re.sub('[!-/:-@[-`{-~、。「」【】#★ﾟ]', '', tweet)
    return tweet


def analysis_tweet(tweets):
    mecab_path = open('./mecab_path', 'r').read().replace('\n', '')
    mecab = MeCab.Tagger('-d {0}'.format(mecab_path))

    words = []
    count = 0
    for tweet in tweets:
        count += 1
        tweet = tweet_clean(tweet.full_text)
        # 空白除外
        analysis_list = [x for x in mecab.parse(tweet).split('\n') if x and x != 'EOS']
        for analysis in analysis_list:
            # 固有名詞かつ笑wーは除外
            if analysis.split('\t')[1].split(',')[1] in ('固有名詞') and analysis.split('\t')[0] not in ['w' * x for x in range(1,20)] + ['笑' * x for x in range(1,20)] + ['ー']:
                words.append(analysis.split('\t')[0])

    # カウントランキングTop10
    rank = collections.Counter(words).most_common(10)
    return rank


def handler(event, context):
    tweets = get_tweet(event['username'])
    if tweets == 429:
        return {
            'statusCode': 429,
            'body': json.dumps('access count error')
        }
    elif tweets == 403:
        return {
            'statusCode': 403,
            'body': json.dumps('user protected')
        }
    else:
        rank = analysis_tweet(tweets)
        return {
            'statusCode': 200,
            'body': json.dumps(rank, ensure_ascii=False)
        }


# if __name__ == "__main__":
#     get_tweet(screen_name='sho171_0')
