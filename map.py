from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('symbol_map.html')

@app.route('/map')  # Creating a new route for the choro_map.html
def map():
    return render_template('choro_map.html')

if __name__ == '__main__':
    app.run(debug=True)
