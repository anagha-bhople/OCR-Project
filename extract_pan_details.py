import re
import pan_aadhar_ocr
from pan_aadhar_ocr import Pan_Info_Extractor


def extract_pan_details(text, filename):
    text_name = None
    text_fname = None
    dob = None
    pan = None
    nameline = []
    fnameline = []
    dobline = []
    panline = []
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
    lineno = 0
    for wordline in text1:
        xx = wordline.split('\n')
        if ([w for w in xx if re.search(
                '(INCOMETAXDEPARWENT|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$',
                w)]):
            text1 = list(text1)
            lineno = text1.index(wordline)
            break
    text0 = text1[lineno + 1:]
    try:

        # Cleaning first names
        text_name = findword(text1, '(oral|Name|name|nam|Nam|ata|NAME|aoe|ATa|oral)$')
        # print(text_name)
        nameline = text_name[0]
        text_name = nameline.rstrip()
        text_name = text_name.lstrip()
        text_name = re.sub('[^a-zA-Z] +', ' ', text_name)
        text_name = ' '.join(filter(str.isupper, text_name.split()))
        # print(text_name)
        if text_name == "":
            nameline = text1[2]
            text_name = nameline.rstrip()
            text_name = text_name.lstrip()
            text_name = re.sub('[^a-zA-Z] +', ' ', text_name)
            text_name = ' '.join(filter(str.isupper, text_name.split()))

        # Cleaning Father's name
        text_fname = findword(text1, '(Father\'s|father\'s|Fathe\'s|Fathers Name)$')
        # print(text_fname)
        fnameline = text_fname[0]
        text_fname = fnameline.rstrip()
        text_fname = text_fname.lstrip()
        text_fname = re.sub('[^a-zA-Z] +', ' ', text_fname)
        text_fname = ' '.join(filter(str.isupper, text_fname.split()))
        # print(text_fname)
        if text_fname == "":
            fnameline = text1[3]
            text_fname = fnameline.rstrip()
            text_fname = text_fname.lstrip()
            text_fname = re.sub('[^a-zA-Z] +', ' ', text_fname)
            text_fname = ' '.join(filter(str.isupper, text_fname.split()))

        extractor = Pan_Info_Extractor()
        pan_info = extractor.info_extractor(filename)
        pan_info = pan_info.split(",")

        # Cleaning DOB
        dob = pan_info[3]
        dob = dob.split(" ")
        dob = dob[2]
        dob = dob.replace('"', " ")
        dob = dob.replace('}', " ")
        dob = dob.lstrip()
        dob = dob.rstrip()
        # print(dob)

        # Cleaning PAN Card details
        pan = pan_info[0]
        pan = pan.split(" ")
        pan = pan[1]
        pan = pan.replace('"', " ")
        pan = pan.lstrip()
        pan = pan.rstrip()
        pan = ' '.join(filter(str.isupper, pan.split()))
        # print(pan)

    except:
        pass
    data = {}
    data['Name'] = text_name
    data['Father Name'] = text_fname
    data['Date of Birth'] = dob
    data['PAN'] = pan
    data['ID Type'] = "PAN"
    return dob, text_fname, text_name, pan


def findword(textlist, wordstring):
    lineno = -1

    for wordline in textlist:
        xx = wordline.split()
        if ([w for w in xx if re.search(wordstring, w)]):
            lineno = textlist.index(wordline)
            if lineno != 0:
                textlist = textlist[lineno + 1:]
                return textlist

    return textlist
