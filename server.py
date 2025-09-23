from flask import Flask, render_template_string, send_from_directory
app = Flask(__name__)

@app.route('/')
def x():
    return render_template_string(open('index.html').read())

@app.route('/<path:y>')
def z(y):
    return send_from_directory('.', y)

if __name__=='__main__':
    app.run(debug=False, port=4000)

