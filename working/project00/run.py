from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    title = "خوش آمدید"
    return render_template('home.html',page_title=title)

@app.route('/about')
def  about():
    return render_template('about.html',page_title = "درباره من")

@app.route('/contact')
def contact():
    return render_template('contact.html',page_title = "تماس با ما")

@app.route('/form',methods=['GET' , 'POST'])
def form_page():
    if request.method == 'POST':
        name = request.form.get('name')
        return render_template('form.html',message=f"سلام {name} عزیز")
    return render_template('form.html',page_title ='ثبت نام')
@app.route('/services')
def services():
    items = [
        {"name": "طراحی", "price": 9171500096},
        {"name": "نقشه برداری", "price": 9171509800},
        {"name": "طراحی", "price": 9171502549}
    ]
    return render_template('services.html',items=items)
@app.errorhandler(404)
def page_not_found(e):
    return  render_template('404.html'), 404
if __name__ =='__main__':
    app.run(debug=True)