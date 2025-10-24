from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/weer')
def weer():
    return render_template('weer.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/statistiek')
def statistiek():
    return render_template('statistiek.html')

if __name__ == '__main__':
    app.run(debug=True)