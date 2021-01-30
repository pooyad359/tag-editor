from flask import Flask, request
import pyexiv2
import json
import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import webbrowser


UPLOAD_FOLDER = 'static/uploads/'


app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ACTIVE_IMAGE_PATH = None

def get_image():
    if ACTIVE_IMAGE_PATH is None:
        return None
    else:
        return pyexiv2.Image(ACTIVE_IMAGE_PATH)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')



@app.route('/', methods=['POST'])
def upload_image():
    global ACTIVE_IMAGE_PATH
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ACTIVE_IMAGE_PATH = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(ACTIVE_IMAGE_PATH)
        print('\t* upload_image filename: ' + filename)
        print(ACTIVE_IMAGE_PATH)
        flash('Image successfully uploaded and displayed')
        image_data_dict = get_image().read_exif()
        # image_data = [f'{k}: {v}' for k,v in image_data_dict.items()]
        return render_template(
            'view.html', 
            filename=filename,
            # image_data = "\n".join(image_data)
            image_data = image_data_dict
            )
        # return redirect(url_for('static', filename='uploads/' + filename), code=301)

    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/submit',methods=['POST'])
def submit():
    print(ACTIVE_IMAGE_PATH)
    new_image_data = request.form
    img = get_image()
    img.modify_exif({
        'Exif.Image.DocumentName': new_image_data['DocumentName'],
        'Exif.Image.ImageDescription':new_image_data['Description'],
    })
    try:
        with open('./files/gps_data.json','r') as fp:
            geo_data = json.load(fp) 
        img.modify_exif(geo_data)
    except:
        pass
    return redirect('/')

@app.route('/display/<filename>')
def display_image(filename):
    #print( 'display_image filename: ' + filename)
    # data = request.form['input_name']
    print(request.form)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/display/<filename>', methods=['POST'])
def submit_changes(filename):
    #print('display_image filename: ' + filename)
    # data = request.form['input_name']
    print(request.form)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)




@app.route('/exit',methods=['GET','POST'])
def exit_app():
    print('\t* Exitting the app')
    os._exit(1)
    return ""

if __name__ == "__main__":
    webbrowser.open_new('http://127.0.0.1:5000/')
    app.run(debug=False)
    