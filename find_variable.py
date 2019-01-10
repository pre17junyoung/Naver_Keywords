from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import pandas as pd
import pickle
import requests, json
import sys, os



def send_slack(msg, channel="#james_new", username="model_bot" ):
    webbook_URL = "https://hooks.slack.com/services/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"
    payload = {
        "channel" : channel,
        "username" : username,
        "icon_emoji" : ":provision",
        "text" : msg,
    }

    response = requests.post(
        webbook_URL,
        data = json.dumps(payload)
    )




def find_accuracy(alpha):
    
    #기사 데이터 프레임 코드
    article_df = pd.read_pickle("{}/article_2016-06-01.plk".format(os.path.dirname(os.path.realpath(__file__))))
    
    # 테스트 데이터와 트레인 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(article_df.content, article_df.category, test_size=0.1, random_state=1)

    # vectorizer & classification algorithm
    clf = Pipeline([
        ('vect', TfidfVectorizer()),
        ('clf', MultinomialNB(alpha=float(alpha)))
    ])

    # 모델 생성
    model = clf.fit(X_train, y_train)

    # 테스트 데이터 예측 결과 출력
    y_pred = model.predict(X_test)

    # 정확도 확인
    result = accuracy_score(y_test, y_pred)
    send_slack("alpha:{}, accuracy:{}".format(alpha, result))
    return result


result = find_accuracy(sys.argv[1])
print(result)






