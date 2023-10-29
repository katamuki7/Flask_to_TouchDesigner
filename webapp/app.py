from flask import render_template, Flask, Response
import cv2 as cv
import os
import pyrebase


config={
    API_KEY
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

def push(x):
    data = {
        "em": x,
    }
    db.child("ems").push(data)

# 環境変数の設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"
# google-cloud-visionモジュールのインポート
from google.cloud import vision
# クライアントの作成
client = vision.ImageAnnotatorClient()

app = Flask(__name__, static_folder='./templates/images')

camera = cv.VideoCapture(0)

likeli_ary = ["喜び", "悲しみ", "怒り", "驚き"]

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            #フレームデータをjpgに圧縮
            ret, buffer = cv.imencode('.jpg',frame)
            # bytesデータ化
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    #imgタグに埋め込まれるResponseオブジェクトを返す
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():

    user = {'username': 'FZ50'}
    return render_template('index.html', title='home', user=user)

@app.route('/result')
def resultpage():

    img_path = 'images/image.jpg'
    cap = cv.VideoCapture(0)
    ret, frame = cap.read()
    cv.imwrite("./templates/images/image.jpg", frame)
    # 画像の読み込み
    image = vision.Image()
    with open("./templates/images/image.jpg", "rb") as f:
        image.content = f.read()
    # 感情分析の実行
    response = client.face_detection(image=image)
    faces = response.face_annotations

    # 結果の表示
    num_likeli = []
    likeli_dic = {}
    #for face in faces:
    face = faces[0]
    emotions = ["joy", "sorrow", "anger", "surprise"]
    likelihoods = [face.joy_likelihood, face.sorrow_likelihood, face.anger_likelihood, face.surprise_likelihood]
    for emotion, likelihood in zip(emotions, likelihoods):
        if likelihood.name == "VERY_UNLIKELY":
            num_likeli.append(1)
        elif likelihood.name == "UNLIKELY":
            num_likeli.append(2)
        elif likelihood.name == "LIKELY":
            num_likeli.append(3)
        else:
            num_likeli.append(4)
    for i in range(4):
        likeli_dic[likeli_ary[i]] = num_likeli[i]
    max_likeli = (max(likeli_dic, key=likeli_dic.get))
    if max_likeli == "喜び":
        x = 1
    elif max_likeli == "悲しみ":
        x = 2
    elif max_likeli == "怒り":
        x = 3
    else:
        x = 4
    print(x)
    push(x)


    return render_template('result.html', image_path=img_path, max_likeli = max_likeli)


if __name__ == "__main__":
    app.run(debug=True)