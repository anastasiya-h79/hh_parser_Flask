from flask import Flask, render_template, request
from m import parser
from alchemy_parser import  parser_alchemy

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/contacts/')
def contacts():
    developer_name = 'https://github.com/anastasiya-h79/'
    return render_template('contacts.html', name=developer_name)


@app.route('/request/', methods=['GET'])
def request_get():
    return render_template('request.html')


@app.route('/results/', methods=['POST'])
def request_post():
    name = request.form['vacancy']
    area = request.form['area']
    request_result = parser_alchemy(name, area)
    return render_template('results.html', data=request_result)


# @app.route('/results/', methods=['POST'])
# def results():


    # with open('request_result.json', "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # # print(data)
    # return render_template('results.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)
