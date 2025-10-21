from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
def weer():
    return render_template('weer.html')
def contact():
    return render_template('contact.html')
def statistiek():
    return render_template('statistieken.html')

if __name__ == '__main__':
    app.run(debug=True)