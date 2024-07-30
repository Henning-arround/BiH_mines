from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('symbol.html')


if __name__ == '__main__':
    with app.test_request_context():
        with open('index.html', 'w') as f:
            f.write(render_template('symbol.html'))
