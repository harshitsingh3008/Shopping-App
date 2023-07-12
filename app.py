import os
from flask import Flask
from flask import render_template,redirect,url_for
from flask import request
from sqlalchemy import Column, Integer, Text, ForeignKey, String
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sample.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class User(db.Model):
    __tablename__="user"
    id = Column(Integer,autoincrement=True,primary_key=True)
    username = Column(String , nullable= False,unique=True)
    password = Column(String, nullable= False)
    #name = Column(String , nullable = False)
    # age = Column(Integer)
    # gender = Column(String)

class Manager(db.Model):
    __tablename___ = "manager"
    id = Column(Integer,autoincrement=True,primary_key=True)
    username = Column(String, nullable= False,unique=True)
    password = Column(String,nullable = False)


class Category(db.Model):
    __tablename__ = "category"
    id = Column(Integer,primary_key = True,nullable=False,autoincrement=True)
    name = Column(String, nullable= False,unique=True)

class Product(db.Model):
    __tablename__ = "product"
    id= Column(Integer,primary_key = True,nullable=False,autoincrement=True)
    name =   Column(String,nullable=False,unique=True)
    unit=    Column(String,nullable=False)
    rate =   Column(Integer,nullable=False)
    quantity=Column(Integer,nullable=False)

class Connection(db.Model):
    __tablename__ = "connection"
    category_id= db.Column(Integer,ForeignKey('category.id'),nullable=False)
    product_id= db.Column(String,ForeignKey('product.id'),nullable=False)
    connection_id = db.Column(db.Integer,autoincrement=True,primary_key=True)

class Sales(db.Model):
    __tablename__ = "sales"
    prod_id = db.Column(Integer,primary_key=True)
    amount = db.Column(Integer)

class Cart(db.Model):
    __tablename__ = "cart"
    prod_id = db.Column(Integer,primary_key=True)
    prod_name = db.Column(String,nullable=False)
    quantity= db.Column(Integer) 
    cate_name = db.Column(String,nullable=False)
    rate = db.Column(Integer,nullable=False)
    unit=db.Column(String,nullable=False)

db.create_all()



unit = ["Rs/Kg","Rs/Litre","Rs/dozen","Rs/gram"]

@app.route("/",methods=["GET","POST"])
def home():
    return render_template("home.html")


@app.route("/user_login",methods=["GET", "POST"])
def user_login():
    if request.method=="GET":
        return render_template("user.html")
    elif request.method=="POST":
        data=request.form
        # user=data['usernamee']
        # pswrd=data['passwordd']
        user = User.query.filter_by(username=data["usernamee"]).first()
        if user:
            password=User.query.filter_by(password=data["passwordd"]).first()
            if password:
                #n=User.query.filter_by(username=user).first()
                Id=user.id
                return redirect(url_for('user_dashboard',id=Id))
                return render_template("user_dashboard.html")
            else:
                p=0
                return render_template("user.html",p=p)
        else:
            u=0
            return render_template("user.html",u=u)
    

@app.route("/register-user",methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register-user.html")
    elif request.method=="POST":
        data = request.form
        user = User.query.filter_by(username=data["usernamee"]).first()
        if user:
            a=0
            return render_template('register-user.html',a=a)
        else:
            new_user = User(
                username = data["usernamee"],
                password = data["passwordd"]
            )
            db.session.add(new_user)
            db.session.commit()
    return redirect(url_for('user_login'))

@app.route("/user_dashboard/<int:id>",methods=["GET", "POST"])
def user_dashboard(id):
    num= User.query.filter_by(id=id).first()
    name=num.username
    cate= Category.query.all()
    d={}
    for c in cate:
        a=c.id
        d[c]=[]
        prod=Connection.query.filter_by(category_id=a).all()
        for p in prod:
            x=p.product_id
            y=Product.query.filter_by(id=x).first()
            d[c].append(y)
    print(d,'@@@7')
    return render_template("user_dashboard.html",name=num,d=d)

@app.route("/pre_buy/<int:id>/<int:cate_id>/<int:prod_id>",methods=["GET","POST"])
def pre_buy(id,cate_id,prod_id):
    name=User.query.filter_by(id=id).first()
    cate = Category.query.filter_by(id=cate_id).first()
    prod = Product.query.filter_by(id=prod_id).first()
    if request.method == "GET" :
        return render_template("pre_buy.html",name=name,cate=cate,prod=prod)
    elif request.method == "POST" :
        quant = request.form.get('quan')
        if int(quant) > prod.quantity:
            z=0
            return render_template("pre_buy.html",name=name,cate=cate,prod=prod,z=z)
        print(type(quant),'@@@8')
        ratee = prod.rate
        total= int(quant)*int(ratee)
        print(total,'@@@9')
        return redirect(url_for('buy',id=id,cate_id=cate_id,prod_id=prod_id,total=total))


@app.route("/buy/<int:id>/<int:cate_id>/<int:prod_id>/<int:total>",methods=["GET","POST"])
def buy(id,cate_id,prod_id,total):
    name=User.query.filter_by(id=id).first()
    cate = Category.query.filter_by(id=cate_id).first()
    prod = Product.query.filter_by(id=prod_id).first()
    return render_template("buy.html",name=name,cate=cate,prod=prod,total=total)


@app.route("/post_buying/<int:id>/<int:cate_id>/<int:prod_id>/<int:total>",methods=["GET","POST"])
def post_buying(id,cate_id,prod_id,total):
    name=User.query.filter_by(id=id).first()
    cate = Category.query.filter_by(id=cate_id).first()
    prod = Product.query.filter_by(id=prod_id).first()
    quan = total/int(prod.rate)
    prod.quantity = prod.quantity - int(quan)

    sale = Sales.query.filter_by(prod_id=prod_id).first()
    if sale:
        sale.amount = sale.amount + int(quan)
    else:
        new_sale = Sales(
            prod_id = prod_id,
            amount = int(quan)
        )
        db.session.add(new_sale)
        
    # cart_items = Cart.query.all()
    # for c in cart_items:
        # db.session.delete(c)
    db.session.commit()
    return render_template("post_buying.html",name=name,cate=cate,prod=prod,total=total)


@app.route("/add_to_cart/<int:id>/<int:cate_id>/<int:prod_id>",methods=["GET","POST"])
def add_to_cart(id,cate_id,prod_id):
    name=User.query.filter_by(id=id).first()
    items = Product.query.filter_by(id=prod_id).first()
    cate = Category.query.filter_by(id=cate_id).first()
    cart= Cart.query.filter_by(prod_id=prod_id).first()
    if cart:
        if int(cart.quantity)<int(items.quantity):
            cart.quantity +=1
    else:
        new_item = Cart(
            prod_id = prod_id,
            prod_name = items.name,
            quantity = 1,
            cate_name = cate.name,
            rate = items.rate,
            unit = items.unit
        )
        db.session.add(new_item)
    db.session.commit()
    
    return redirect(url_for('user_dashboard',id=id))


@app.route("/cart/<int:id>",methods=["GET","POST"])
def cart(id):
    name=User.query.filter_by(id=id).first()
    items = Cart.query.all()
    grand_total=0
    products=[]
    for i in items:
        products.append(i)
        a,b=int(i.quantity),int(i.rate)
        sum = a*b
        grand_total = grand_total + sum
    print(products,products[0],products[0].prod_name,'@@@11')
    return render_template("cart.html",name=name,products=products,grand_total=grand_total)

@app.route("/edit_cart_item/<int:id>/<int:prod_id>",methods=["GET","POST"])
def edit_cart_item(id,prod_id):
    name=User.query.filter_by(id=id).first()
    return render_template("edit_cart_item.html",name=name)

@app.route("/delete_cart_item/<int:id>/<int:cart_id>",methods=["GET","POST"])
def delete_cart_item(id,cart_id):
    cart_item = Cart.query.filter_by(prod_id=cart_id).first()
    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('cart',id=id))


@app.route("/bought_from_cart/<int:id>",methods=["GET","POST"])
def bought_from_cart(id):
    name=User.query.filter_by(id=id).first()
    cart_item = Cart.query.all()
    d={}
    grand_total=0
    for i in cart_item:
        prod_id = i.prod_id
        a,b=int(i.quantity),int(i.rate)
        sum = a*b
        grand_total = grand_total + sum
        d[i.prod_name] = [i.rate,i.unit,sum]

        sale = Sales.query.filter_by(prod_id=prod_id).first()
        if sale:
            sale.amount = sale.amount + int(i.quantity)
        else:
            new_sale = Sales(
                prod_id = prod_id,
                amount = int(i.quantity)
            )
            db.session.add(new_sale)


        db.session.delete(i)
    db.session.commit()
    return render_template('bought_from_cart.html',name=name,d=d,grand_total=grand_total)


@app.route("/logout",methods=["GET", "POST"])
def logout():
    cart_items = Cart.query.all()
    for c in cart_items:
        db.session.delete(c)
    db.session.commit()
    return render_template('home.html')
    
@app.route("/manager",methods=["GET", "POST"])
def manage():
    if request.method=="GET":
        return render_template("manager.html")
    elif request.method=="POST":
        data=request.form
        # user=data['usernamee']
        # pswrd=data['passwordd']
        user = Manager.query.filter_by(username=data["usernamee"]).first()
        if user:
            password=Manager.query.filter_by(password=data["passwordd"]).first()
            if password:
                return redirect(url_for('manager_dashboard'))
            else:
                p=0
                return render_template("manager.html",p=p)
        else:
            u=0
            return render_template("manager.html",u=u)
 
    
@app.route("/manager_dashboard",methods=["GET", "POST"])
def manager_dashboard():
    data= Category.query.all()
    manager=Manager.query.first()
    name= manager.username
    conn= Connection.query.all()
    print(conn,data,'@@@5')
    l=[]
    for c in conn:
        l.append(c.category_id)
    print(l,'@@@4')
    return render_template("manager_dashboard.html",data=data,user=name,l=l)


@app.route("/create_category",methods=["GET", "POST"])
def category():
    manager=Manager.query.first()
    name= manager.username
    if request.method == "GET":
        return render_template("create_category.html",name=name)
    if request.method == "POST":
        data = request.form
        user = Category.query.filter_by(name=data["cate"]).first()
        if user:
            a=0
            return render_template("create_category.html",a=a,name=name)
        else:
            new_cate = Category(
                name = data['cate']
            )
            db.session.add(new_cate)
            db.session.commit()
    return redirect(url_for('manager_dashboard'))

@app.route("/create_product/<int:id>",methods=["GET", "POST"])
def product(id):
    manager=Manager.query.first()
    name= manager.username
    cate = Category.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("create_product.html",unit=unit,cate=cate,name=name)
    elif request.method == "POST" :
        data = request.form
        num= Product.query.filter_by(name=data['namee']).first()
        if num:
            x=0
            return render_template("create_product.html",unit=unit,cate=cate,x=x,name=name)
        else:
            new_product = Product(
                name =   data['namee'],
                unit=   data['unit'],
                rate =   data['rate'],
                quantity= data['quan']
            )
            db.session.add(new_product)
            db.session.commit()
            print(data['namee'])
    
            a=Product.query.filter_by(name=data['namee']).first()
            conn= Connection(
                category_id= cate.id,
                product_id= a.id
            )
            db.session.add(conn)
            db.session.commit()
            print(new_product,'22222')
    return redirect(url_for('manager_dashboard'))

@app.route("/edit_products/<int:id>",methods=["GET", "POST"])
def edit(id):
    manager=Manager.query.first()
    name= manager.username
    cate= Connection.query.filter_by(category_id=id).all()
    products=[]
    for c in cate:
        e=Product.query.get(c.product_id)
        products.append(e)
    print(cate, '@@@@3', products)
    return render_template("edit_products.html",products=products,name=name)


@app.route("/update_product/<int:id>",methods=["GET","POST"])
def update(id):
    manager=Manager.query.first()
    name= manager.username
    data=Product.query.filter_by(id=id).first()
    print(data,'@@@1')
    if request.method == 'GET':
        return render_template("update_product.html",data=data,unit=unit,name=name)
    if request.method == "POST":
        value = request.form
        update = Product.query.filter_by(id=id).first()
        update.name= value['namee']
        update.unit = value['unit']
        update.rate = value['rate']
        update.quantity = value['quan']

        db.session.commit()
    return redirect(url_for('edit',id=id))

@app.route("/delete_product/<int:id>",methods=["GET","POST"])
def delete_product(id):
    data = Product.query.filter_by(id=id).first()
    num = Connection.query.filter_by(product_id=id).first()
    a=num.category_id
    print(data,num,'@@@2')
    db.session.delete(data)
    
    db.session.delete(num)
    db.session.commit()
    return redirect(url_for('edit',id=a))


@app.route("/edit_category/<int:id>",methods=["GET","POST"])
def edit_category(id):
    manager=Manager.query.first()
    name= manager.username
    data=Category.query.filter_by(id=id).first()
    print(data,'@@@6')
    if request.method == 'GET':
        return render_template("edit_category.html",data=data,name=name)
    if request.method == "POST":
        value = request.form
        update = Category.query.filter_by(id=id).first()
        print(update.name,'$$$')
        update.name= value['cate']

        db.session.commit()
    return redirect(url_for('manager_dashboard'))

@app.route("/delete_category/<int:id>",methods=["GET","POST"])
def delete_category(id):
    data = Category.query.filter_by(id=id).first()
    num = Connection.query.filter_by(category_id=id).all()
    for n in num :
        db.session.delete(n)

    print(data,num,'@@@2')
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('manager_dashboard'))

@app.route("/summary",methods=["GET","POST"])
def summary():
    manager=Manager.query.first()
    name= manager.username
    sales = Sales.query.all()
    d={}
    total=0
    for i in sales:
        prod=Product.query.filter_by(id=i.prod_id).first()
        prod_name = prod.name
        price = int(prod.rate)*int(i.amount)
        total =  total + int(i.amount)*int(price)
        d[prod_name]=[int(i.amount),price]

    print(d,'@@@11')
    return render_template("summary.html",name=name,d=d,total=total)
    
if __name__=="__main__":
    app.run(debug=True)