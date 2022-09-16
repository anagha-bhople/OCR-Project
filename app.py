from flask import Flask, render_template, request
import sqlite3 as sql
import cv2
from PIL import Image
# import tesserocr as tr
from extract_pan_details import extract_pan_details
from extract_aadhar_details import extract_aadhar_details
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
import pytesseract
import os

# define a folder to store and later serve the images
UPLOAD_FOLDER = os.path.join("./files/")

# connect to sql database
con = sql.connect('OCR.db')

# create table if not exists
con.execute(
    'CREATE TABLE IF NOT EXISTS OCR (username TEXT, entity_dob TEXT, entity_father_name TEXT, entity_name TEXT, entity_pan_no TEXT, entity_type TEXT )')
print("Table created successfully")
con.close()

# connect to sql database
con = sql.connect('OCR_1.db')

# create table if not exists
con.execute(
    'CREATE TABLE IF NOT EXISTS OCR_1 (username TEXT, name TEXT, aadhar_no TEXT, gender TEXT, dob TEXT, pincode TEXT, type TEXT)')
print("Table created successfully")
con.close()

# specify allowed file formats
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'pdf'])
OTHER_EXTENSIONS = set(['pdf'])

app = Flask(__name__)


# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# save data in output text file
def output_file(filename, data):
    file = open(filename, "w+")
    file.write(data)
    file.close()


def process_image(iamge_name):
    return pytesseract.image_to_string(Image.open(iamge_name))


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/pan', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':

        # check if there is a file in the request
        if 'file_pan' not in request.files:
            return render_template('upload.html', msg='No file selected')

        file = request.files['file_pan']

        # if no file is selected
        if file.filename == '':
            return render_template('upload.html', msg='No file selected')
        else:
            file.save(UPLOAD_FOLDER + file.filename)

        # if file format is allowed
        if file and allowed_file(file.filename):

            username = request.form['name']

            # if file format is pdf
            if file.filename.rsplit('.', 1)[1].lower() in OTHER_EXTENSIONS:
                name = file.filename.split(".")[0]
                files = convert_from_path(UPLOAD_FOLDER + file.filename, 500)
                for f in files:
                    f.save(UPLOAD_FOLDER + name, 'jpeg')
                    file_1 = cv2.imread(UPLOAD_FOLDER + name)
            else:
                file_1 = cv2.imread(UPLOAD_FOLDER + file.filename)

            text = process_image(UPLOAD_FOLDER + file.filename)
            print(text)

            msg3 = ""
            msg1 = ""

            # check if uploaded document is pancard or not
            if "income" in text.lower() or "tax" in text.lower() or "department" in text.lower():
                dob, fname, name, pan_no = extract_pan_details(text, (UPLOAD_FOLDER + file.filename))
                print(dob, fname, name, pan_no)

                # check if username is valid
                if username.lower() not in name.lower():
                    msg1 = "Invalid User"
                else:
                    msg3 = "Valid User"

                    # saving text document in output folder
                    output_file(UPLOAD_FOLDER + username, text)

                # data insertion in database
                with sql.connect("OCR.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO OCR (username, entity_dob, entity_father_name, entity_name, entity_pan_no, entity_type ) VALUES (?,?,?,?,?,?)",
                        (username, dob, fname, name, pan_no, "PAN"))
                    con.commit()
                    print("Record successfully added")

                # extract the text and display it
                return render_template('upload.html',
                                       msg1=msg1,
                                       msg3=msg3,
                                       msg='Successfully Uploaded'
                                       )
            else:
                msg2 = "Not a pancard"
                return render_template('upload.html',
                                       msg2=msg2
                                       )
    elif request.method == 'GET':
        return render_template('upload.html')


@app.route('/aadhar', methods=['GET', 'POST'])
def upload_page_aadhar():
    if request.method == 'POST':

        # check if there is a file in the request
        if 'file_aadhar_front' not in request.files:
            return render_template('upload_aadhar.html', msg='No file selected')

        if 'file_aadhar_back' not in request.files:
            return render_template('upload_aadhar.html', msg='No file selected')

        file_af = request.files['file_aadhar_front']
        file_ab = request.files['file_aadhar_back']

        # if no file is selected
        if file_af.filename == '':
            return render_template('upload_aadhar.html', msg='No file selected')
        else:
            file_af.save(UPLOAD_FOLDER + file_af.filename)

        if file_ab.filename == '':
            return render_template('upload_aadhar.html', msg='No file selected')
        else:
            file_ab.save(UPLOAD_FOLDER + file_ab.filename)

        # if file format is allowed
        if file_af and allowed_file(file_af.filename):
            if file_ab and allowed_file(file_af.filename):

                username = request.form['name']

                # if file format is pdf
                if file_af.filename.rsplit('.', 1)[1].lower() in OTHER_EXTENSIONS:
                    name = file_af.filename.split(".")[0]
                    files = convert_from_path(UPLOAD_FOLDER + file_af.filename, 500)
                    for f in files:
                        f.save(UPLOAD_FOLDER + name, 'jpeg')
                        file_1 = cv2.imread(UPLOAD_FOLDER + name)
                else:
                    file_1 = cv2.imread(UPLOAD_FOLDER + file_af.filename)

                    # if file format is pdf
                    if file_ab.filename.rsplit('.', 1)[1].lower() in OTHER_EXTENSIONS:
                        name = file_ab.filename.split(".")[0]
                        files = convert_from_path(UPLOAD_FOLDER + file_ab.filename, 500)
                        for f in files:
                            f.save(UPLOAD_FOLDER + name, 'jpeg')
                            file_2 = cv2.imread(UPLOAD_FOLDER + name)
                    else:
                        file_2 = cv2.imread(UPLOAD_FOLDER + file_ab.filename)

                text_front = process_image(UPLOAD_FOLDER + file_af.filename)
                text_back = process_image(UPLOAD_FOLDER + file_ab.filename)

                msg1 = ""
                msg3 = ""

                name, aadhar_no, gender, dob, pincode = extract_aadhar_details(text_front, text_back,
                                                                               (UPLOAD_FOLDER + file_af.filename),
                                                                               (UPLOAD_FOLDER + file_ab.filename))
                print(name, aadhar_no, gender, dob, pincode)

                # check if username is valid
                if username.lower() not in name.lower():
                    msg1 = "Invalid User"
                else:
                    msg1 = "Valid User"

                    # saving text document in output folder
                    output_file(UPLOAD_FOLDER + username, text_front)
                    output_file(UPLOAD_FOLDER + username, text_back)

                # data insertion in database
                with sql.connect("OCR_1.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO OCR_1 (username, name, aadhar_no, gender, dob, pincode, type) VALUES (?,?,?,?,?,?,?)",
                        (username, name, aadhar_no, gender, dob, pincode, "Aadhar"))
                    con.commit()
                    print("Record successfully added")

                # extract the text and display it
                return render_template('upload_aadhar.html',
                                       msg1=msg1,
                                       msg3=msg3,
                                       msg='Successfully Uploaded'
                                       )

    elif request.method == 'GET':
        return render_template('upload_aadhar.html')


@app.route('/data')
def list():
    con = sql.connect("OCR.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from OCR")
    rows = cur.fetchall()
    return render_template("index.html", rows=rows)


@app.route('/data1')
def list1():
    con1 = sql.connect("OCR_1.db")
    con1.row_factory = sql.Row
    cur1 = con1.cursor()
    cur1.execute("select * from OCR_1")
    rows1 = cur1.fetchall()
    return render_template("index1.html", rows=rows1)


if __name__ == '__main__':
    app.run()
