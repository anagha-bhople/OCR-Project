import re
import json
import pytesseract
import cv2
import numpy as np
import sys
import re
import os
from PIL import Image
import io
from pan_aadhar_ocr import Aadhar_Info_Extractor


def extract_aadhar_details(text, text_back, front, back):
    res = text.split()
    name = None
    dob = None
    dob_final = 0
    aadhar_no = 0
    gender = ""
    dob = ""
    number = ""
    pincode = ''
    final_name = ""
    adh = None
    pincode = ""
    text0 = []
    text1 = []
    text2 = []
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n', '')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    text1 = list(filter(None, text1))
    text0 = text1[:]

    lines1 = text_back.split('\n')
    for lin1 in lines1:
        s1 = lin1.strip()
        s1 = lin1.replace('\n', '')
        s1 = s1.rstrip()
        s1 = s1.lstrip()
        text2.append(s1)

    text2 = list(filter(None, text2))
    text3 = text2[:]

    try:

        k = 0
        # Cleaning first names
        name = text0[1]
        name = name.rstrip()
        name = name.lstrip()
        name = name.replace("8", "B")
        name = name.replace("0", "D")
        name = name.replace("6", "G")
        name = name.replace("1", "I")
        name = re.sub('[^a-zA-Z] +', ' ', name)
        name_1 = name.split()
        for i in name_1:
            if i[0].isupper() == True:
                final_name = name
                k = 1
            else:
                k = 0
                break
        if k == 0:
            name = text0[2]
            name = name.rstrip()
            name = name.lstrip()
            name = name.replace("8", "B")
            name = name.replace("0", "D")
            name = name.replace("6", "G")
            name = name.replace("1", "I")
            name = re.sub('[^a-zA-Z] +', ' ', name)
            name_1 = name.split()
            for i in name_1:
                if i[0].isupper() == True:
                    final_name = name
                    k = 1
                else:
                    k = 0
                    break
        if k == 0:
            name = text0[3]
            name = name.rstrip()
            name = name.lstrip()
            name = name.replace("8", "B")
            name = name.replace("0", "D")
            name = name.replace("6", "G")
            name = name.replace("1", "I")
            name = re.sub('[^a-zA-Z] +', ' ', name)
            name_1 = name.split()
            for i in name_1:
                if i[0].isupper() == True:
                    final_name = name
                    k = 1
                else:
                    k = 0
                    break
    except:
        pass

    try:

        # Cleaning pincode  details
        for word in text2:
            data_pin = word.split()
            for i in data_pin:
                if len(i) == 6 and i.isdigit():
                    pincode = pincode + i + ' '
        pincode = pincode.split()[0]

    except:
        pass

    try:

        extractor = Aadhar_Info_Extractor()
        aadhar_info = extractor.info_extractor(front, back)
        aadhar_info = aadhar_info.split(",")

        # Cleaning DOB
        dob_1 = aadhar_info[3]
        dob = gender.join(dob_1)
        dob = dob.split('"')
        dob = dob[3]

        # Cleaning aadhar number
        number = ""
        aadhar_no = aadhar_info[0]
        number = number.join(aadhar_no)
        number = number.split('"')
        number = number[3]

        # Cleaning gender
        gender = ""
        gender_1 = aadhar_info[2]
        gender = gender.join(gender_1)
        gender = gender.split('"')
        gender = gender[3]

    except:
        pass

    return final_name, number, gender, dob, pincode


def findword(textlist, wordstring):
    lineno = -1
    for wordline in textlist:
        xx = wordline.split()
        if ([w for w in xx if re.search(wordstring, w)]):
            lineno = textlist.index(wordline)
            textlist = textlist[lineno:]
            return textlist
    return textlist
