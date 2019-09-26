from google.cloud import vision
import io
import pandas as pd


def check_string(string):
    
    string = ''.join(e for e in string if e.isalnum() or e =='-')

    error = 0
    string = string.split('-')
    while '' in string: 
        string.remove('')    
    
    # it can happen that the plate number appears before the license, this checks it
    if len(f) == 2:
        f = sorted(f, key=len)
        f = '-'.join(f)
    elif len(f) == 3:
        f = sorted(f, key=len)
        f = [f[1],f[0],f[2]]
        f = '-'.join(f)

    else:
        string = '-'.join(string)
    license = ''
    plate = ''
    for i in range(len(string)):
        # the first number should correspond to the beginning of the plate 
        if string[i].isdigit():
            license = string[0:i]
            plate = string[i:]
            break
    
    # remove eventual extras '-'
    if license and license[-1] == '-':
        license = license[:-1]
    if plate and plate[-1] == '-':
        plate = plate[:-1]

    # checks if license and plate have a possible number and type of chars
    if license == '' or len(license) < 4 or len(license) > 6 or not license.isupper():
        error = 1

    if plate == '' or len(plate) < 2 or len(plate) > 4 or not plate.isdigit():
        error = 1
    return license, plate, error


def detect_text(path,ID,df):
    """Detects text in the file."""
    
    client = vision.ImageAnnotatorClient()
    
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        
        
        print(text.description)
        print('--------')
    if texts:
        license, plate, error = check_string(texts[0].description.replace('\n','-').replace(' ','-'))
        df = df.append({'License_ID': ID, 'license': license, 'plate': plate, 'error': error}, ignore_index=True)
    else:
            df = df.append({'License_ID': ID, 'license': '', 'plate': '', 'error': 1}, ignore_index=True)
    return df
    

df = pd.DataFrame(columns = ['License_ID', 'license', 'plate', 'error'])         
for i in range(0,294):
    df = detect_text(f'./../dataset_particulars/licenses/test/{i}.png',i,df)
print(df)    
df.to_csv('./../resultsgoogle_results_license.csv', index= False)