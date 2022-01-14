from flask import Flask, redirect


app = Flask(__name__, static_url_path="", static_folder="../static")


@app.route('/', methods=['GET'])
def default_request():
    return redirect("/index.html")


if __name__ == '__main__':
    app.run(threaded=True, port=5000)  # threaded=True for multiple user access
