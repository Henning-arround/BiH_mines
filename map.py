from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('symbol.html')

@app.route('/choro')
def symbol():
    return render_template('choro.html')

if __name__ == '__main__':
    app.run(debug=True)
