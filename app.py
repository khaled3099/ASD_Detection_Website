import os

import numpy as np
from PIL import Image
from flask import Flask, render_template, url_for, redirect
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField, FileField
from wtforms.validators import InputRequired, Length, ValidationError
import tensorflow as tf
loaded_model = tf.keras.models.load_model('C:/Users/Famille/Desktop/ProjetPFA/ProjetPFA/ProjetFinAnne/model92.h5')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy()
bcrypt = Bcrypt(app)
# Update the SQLAlchemy URI to use MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/autivision'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
app.config['SECRET_KEY'] = 'this is a secret key'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    __tablename__ = 'registered_users'

from wtforms.fields.simple import PasswordField

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                             render_kw={"placeholder": "Password"})  # Change StringField to PasswordField

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
            raise ValidationError("This username already exists. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                             render_kw={"placeholder": "Password"})  # Change StringField to PasswordField

    submit = SubmitField("Login")



class UploadForm(FlaskForm):
    image = FileField(validators=[InputRequired()])
    submit = SubmitField("Upload")



@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about')
def about(): 
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
from flask import render_template, request, jsonify
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    r = None  
    message = ''
    if request.method == 'POST':
        if 'image' not in request.files:
            message = 'No file part'
        else:
            file = request.files['image']
            if file.filename == '':
                message = 'No selected file'
            else:
                print("Received image:", file.filename)  # Debugging statement
                # Save the uploaded file
                imgo = Image.open(file)
                img_array = load_and_preprocess_image(imgo)
                print("Image array shape:", img_array.shape)  # Debugging statement
                prediction_result = loaded_model.predict(img_array)
                pa = 1 - float(prediction_result) # probability Autistic 
                pas = "{:.2f}".format(pa)  # probability Autistic String 
                pn = float(prediction_result) # probability Non Autistic
                pns = "{:.2f}".format(pn) # probability Non Autistic String
                if prediction_result > 0.3:
                    r = f"Autistic : {pas}% \n Non Autistic : {pns}%"
                    r1 = r.replace("\n", "<br>")
                else:
                    r = f"Autistic : {pas}% \n Non Autistic : {pns}%"
                    r1 = r.replace("\n", "<br>")
                print("Prediction result:", r1)  # Debugging statement
                message = 'File uploaded successfully'
                
                return jsonify({'result': r1, 'message': message})

    # If there's no prediction result yet, return an empty response
    return render_template('dashboard.html')



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('welcome'))
    return render_template('login.html', form=form)
    
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

from flask import jsonify

@app.route('/dashboard_2', methods=['GET', 'POST'])
@login_required
def dashboard_2():

    image_dir = "C:/Users/Famille/Desktop/ProjetPFA/ProjetPFA/ProjetFinAnne/static/uploads"
    images = os.listdir(image_dir)

    class_0_images = []
    class_1_images = []

    if request.method == 'POST':
        delete_items(image_dir)
        uploaded_files = request.files.getlist('images[]')
        print("uploaaaaaaaaaded : ",uploaded_files)
        for file in uploaded_files:
            filename = file.filename
            print("file naaaaaaaaaaaaaaame ::: ",filename)
            index = filename.find('/')
            if index != -1:
                filename1 = filename[index + 1:]
            else:
                filename1 = filename
            file_path = os.path.join(image_dir, filename1)
            print("file paaaaaaaaaaath ::: ",file_path)
            file.save(file_path)

        #for img_name in images:
         #   img_path = os.path.join(image_dir, img_name)
            
          #  print("Image Path:", img_path)  # Debug: Print image path

            # Load and preprocess the image
            with Image.open(file_path) as im:
                img = load_and_preprocess_image(im)  # Assuming you have a function for this
                print("Image Shape:", img.shape)  # Debug: Print image shape

            # Make prediction
            prediction_result = loaded_model.predict(img)  # Assuming loaded_model is defined elsewhere
            print("Prediction Result:", prediction_result)  # Debug: Print prediction result

            # Classify image based on prediction
            if prediction_result > 0.3:
                class_0_images.append(filename1)  # Add image to class 0
            else:
                class_1_images.append(filename1)  # Add image to class 1

        print("Class 0 Images:", class_0_images)  # Debug: Print class 0 images
        print("Class 1 Images:", class_1_images)  # Debug: Print class 1 images

        # Return the lists as JSON data
        return jsonify({'class_0_images': class_0_images, 'class_1_images': class_1_images})

    # If the request method is GET, render the template with the list of images
    return render_template('dashboard_2.html', images=images)

def delete_items(directory):
    # Iterate over all the files in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        os.remove(item_path)



def load_and_preprocess_image(img):
    imag = img.resize((224, 224))  # Resize image if necessary
    img_array = np.array(imag)
    img_array = img_array / 255.0  # Normalize pixel values to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array




if __name__ == '__main__':
    app.run(debug=True)
