import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import sqlite3
import requests
import query

app = Flask(__name__)
ask = Ask(app, "/")
API_URL =  "https://api.cognitive.microsoft.com/bing/v5.0/news/search\?q\={query}\&count\=10\&offset\=0\&mkt\=en-us\&safeSearch\=Moderate"
# logging.getLogger("flask_ask").setLevel(logging.DEBUG)

class Message:

    def welcome_new_user(self):
        msg = 'Welcome to Chai pe Charcha!'\
              'See the news of places near you'\
              ' and affect you the most! Give your opinion '\
              ' every one can give opinion on the issues, upvote'\
              'the opinion you find most helpful!'\
        return msg

    def welcome_existing_user(self):
        msg = 'Welcome back Chai pe Charcha!'\
              'See the news of places near you'
        return msg

    def ask_location(self, location):
        msg = 'Chai pe charcha needs to process the news for you'\
              ', Using your location given by amazon account, your'\
              ' location is set as {}'.format(location)
        return msg


msg = Message()

# database
users = query.execute("""
    SELECT user_id,
           newsCount,
           location
      FROM user
    """)
rows = [dict(user) for user in users.fetchall()]
users = dict()
for row in rows:
    user = dict(
        newsCount=row["newsCount"],
        location=row["location"]
    )
    users[row["user_id"]] = user


def create_new_user(userId, location):
    query.execute("""
        INSERT INTO user
             VALUES (user_id, newsCount, location)
    """, (userId, -1, location))
    return {
        'newsCount': -1,
        'location': location,
    }


@ask.launch
def new_game():
    userId = session.user['userId']
    global userId
    location = 'seattle'
    print('USERS: ', users)
    print('USER ID: ', userId)
    if userId not in users:
        users[userId] = create_new_user(userId, location)
        msg = msg.welcome_new_user() + msg.ask_location()
    else:
        msg = msg.welcome_existing_user()
    return question(msg)

@ask.intent('StreamNewsIntent')
def stream_news():
    news = requests.get(API_URL.format(query=users[userID]['location']), headers={"Ocp-Apim-Subscription-Key": "7f063e7d5c3f44faa51d85f77dc9cf25"})
    news = dict(news.json())
    # One of problems here:
        ## 1. Bing provides the description of the news, however its not complete text. Few sentences only with a trailing ...


@ask.intent("RecordOpinion")
def record(opinion):
    pass

news = [
    {
        'title': 'this is the awesome news number 1',
        'comments': [
            'this is comment 1',
            'this is comment 2',
        ]
    },
    {
        'title': 'this is the genius news number 2',
        'comments': [
            'this is comment 1',
            'this is comment 2'
        ]
    },
    {
        'title': 'This is furious news coming at you at number 3',
        'comments': [
        ]
    },
    {
        'title': 'Shirenie Aoi shiori, life in a glass house, news number 4',
        'commments': [
            'this is comment 1',
            'this is comment 2'
        ]
    }
]

@ask.intent("NewsIntent")
def broadcast():
    if 'news_no' in session.attributes:
        session.attributes['news_no'] += 1
    else:
        session.attributes['news_no'] = 0

    n = session.attributes['news_no']
    if n < len(news):
        return question(news[n]['title'])
    else:
        return question('You are up-to-date with news articles')

@ask.intent('ViewCommentsIntent')
def view_comment():
    cur_new = session.attributes['news_no']
    return question('. '.join(news[cur_new]['comments']))

@ask.intent('PostOpinionIntent')
def new_comment(opinion):
    print('OPINION: ', opinion)
    return question('Your opinion has been posted')

@ask.intent("YesIntent")
def next_round():
    # numbers = [randint(0, 9) for _ in range(3)]
    # round_msg = render_template('round', numbers=numbers)
    # session.attributes['numbers'] = numbers[::-1]  # reverse
    # return question(round_msg)
    base = randint(0,9)
    length = randint(1,5)
    ceil = base + length
    random_number_range = [i for i in range(base, ceil+1)]
    random_number = randint(base, ceil)
    session.attributes['random'] = random_number
    print('Random number is ', random_number)
    return question('I have a number in mind, from the range {0} to {1},'\
                    'Can you guess the number?'.format(base, ceil))

@ask.intent("NoIntent")
def leave_gracefully():
    return statement('losers are quitters, spread salt on your sorry buttocks man')

@ask.intent("AnswerIntent", convert={'choice': int})
def choice(choice):
    if choice==session.attributes['random']:
        return question('Wow! you are a genius, want to test again?')
    else:
        return question('damn it sucks, the right answer was {}, try again?'.format(session.attributes['random']))


# @ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
# def answer(first, second, third):
    # # winning_numbers = session.attributes['numbers']
    # # if [first, second, third] == winning_numbers:
        # # msg = render_template('win')
    # # else:
        # # msg = render_template('lose')
    # # return statement(msg)
    # return statement('hopefully this works')

if __name__ == '__main__':
    app.run(debug=True)
