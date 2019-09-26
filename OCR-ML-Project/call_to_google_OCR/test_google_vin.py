from google.cloud import vision
import io
import pandas as pd


def len_numbers_at_end(string):
    cont = 0
    for i in range(len(string)-1,0,-1):
        if not string[i].isdigit():
            break
        cont +=1
    return cont


def len_letters_at_begin(string):
    cont = 0
    for i in range(0,len(string)):
        if not string[i].isalpha() and not string[i].isupper():
            break
        cont +=1
    return cont


def check_string(string):
    
    string = ''.join(e for e in string if e.isalnum() or e =='@')
        
    error = 0
    string = string.split('@')
    string = sorted(string, key= len, reverse = True)[0]
    
    while '@' in string: 
        string.remove('@')
          
    # there could be the little 'E' in some pictures, grouped with the vin
    if len(string) == 18:
        string = string[1:]
        
    # a correct vin has always 17 chars
    if len(string) != 17:
        error = 1
    else:
        letters = len_letters_at_begin(string)
        nums = len_numbers_at_end(string)
        
        if letters < 1 or letters > 11:
            error = 1
        if nums < 5 or nums > 14:
            error = 1

    return string, error


def detect_text(path,ID, df):
    """Detects text in the file."""
    
    client = vision.ImageAnnotatorClient()
    
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    try:
        response = client.text_detection(image=image)
    except:
        print('No text detected')
        df = df.append({'Vin_ID': ID, 'VIN': '','error': 1}, ignore_index=True)
        return df
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
     
        print(text.description)
        print('--------')
        
    if texts:
        vin, error = check_string(texts[0].description.replace('\n','@').replace(' ','@'))
        print(vin + ' --- ' + str(error))
        df = df.append({'Vin_ID': ID, 'VIN': vin,'error': error}, ignore_index=True)
    else:
        df = df.append({'Vin_ID': ID, 'VIN': '','error': 1}, ignore_index=True)
    return df
    

df = pd.DataFrame(columns = ['Vin_ID', 'VIN', 'error'])         
for i in range(0,294):
    print(i)
    df = detect_text(f'./../dataset_particulars/vins/test/{i}.png',i, df)
print(df)    
df.to_csv('./../results/google_results_vin2.csv', index= False)