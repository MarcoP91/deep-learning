from google.cloud import vision
import io
import pandas as pd


def check_period(split_part, time):
    if not split_part.isdigit():
        return 1
    if time == 'd':
        if int(split_part) < 1 or int(split_part) > 31:
            return 1
    elif time == 'm':
        if int(split_part) < 1 or int(split_part) > 12:
            return 1       
    else:
        if int(sp) < 2014 or int(split_part) > 2019:
            return 1
    return 0
  
    
def remove_extra_points(string):
    is_previous_point = False
    new_string = ''
    for i in range(len(string)):
        if string[i] == '.':
            if not is_previous_point:
                is_previous_point = True
                new_string += string[i]
            else:
                pass
        else:
            is_previous_point = False
            new_string += string[i]

    return new_string


def check_string(string):
    
    error = 0 
    
    # a point could be easily identified as something else
    
    string = string.replace(';','.')
    string = string.replace(',','.')
    string = string.replace(':','.')
    string = string.replace(' ', '.')
    
    # the parts of the date could be separated by more than one point
    string = remove_extra_points(string)
    
    # remove eventual symbols or letters at beginning
    if not string[0].isdigit():
        string = string[1:]
    if not string[-1].isdigit():
        string = string[:-1]
    
    split = string.split('.')
    while '' in split: 
        split.remove('') 
    
    if len(split) == 3:
        # 2 points found
        if len(split[0]) == len(split[1]) == 2 and (len(split[2]) == 2 or len(split[2])== 4):
            if len(split[2]) == 2:
                # we want the year in 201X form
                year = '20' + split[2]
                split = [split[0], split[1], year]
            error += check_period(split[0],'d')
            error += check_period(split[1],'m')
            error += check_period(split[2],'y')
            string = '.'.join(split)
            
        else:
            error = 1
            
    elif len(split) == 2: 
        # only one point found
        # a correct date missing only one point has either 7 or 9 chars
        if len(split[0]) + len(split[1]) + 1 == 7:
            #if the second point is the one missing
            if len(split[0]) == 2:
                year = '20' + split[1][2:]
                new_split = [split[0],split[1][:2],year]
                error += check_period(new_split[0],'d')
                error += check_period(new_split[1],'m')
                error += check_period(new_split[2],'y')
                string = '.'.join(new_split)
            #if the first point is the  one is missing
            elif len(split[1]) == 2:
                year = '20' + split[1]
                new_split = [split[0][:2],split[0][2:],year]
                error += check_period(new_split[0],'d')
                error += check_period(new_split[1],'m')
                error += check_period(new_split[2],'y')
                string = '.'.join(new_split)
            else:
                error = 1
        
        elif len(split[0]) + len(split[1]) + 1 == 9:
            #if the second point is the one missing
            if len(split[0]) == 2:
                new_split = [split[0],split[1][:2],split[1][2:]]
                error += check_period(new_split[0],'d')
                error += check_period(new_split[1],'m')
                error += check_period(new_split[2],'y')
                string = '.'.join(new_split)
            #if the first point is the  one is missing
            elif len(split[1]) == 4:
                new_split = [split[0][:2],split[0][2:],split[1]]
                error += check_period(new_split[0],'d')
                error += check_period(new_split[1],'m')
                error += check_period(new_split[2],'y')
                string = '.'.join(new_split)
            else:
                error = 1  
    else:
        error =1
    
    return string, error


def detect_text(path,ID, df):
    """Detects text in the file."""
    
    client = vision.ImageAnnotatorClient()
    try:
        with io.open(path, 'rb') as image_file:
            content = image_file.read()
    except:
        print('File not found')
        df = df.append({'Date_ID': ID, 'registration': '','error': 1}, ignore_index=True)
        return df
    image = vision.types.Image(content=content)
    try:
        response = client.text_detection(image=image)
    except:
        print('No text found')
        df = df.append({'Date_ID': ID, 'registration': '','error': 1}, ignore_index=True)
        return df
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
            
        print(text.description)
        print('--------')
        
    if texts:
        # take the date between all the text detected
        date = texts[0].description.replace('\n','@').replace(' ','.')
        date = date.split('@')
        date = sorted(date, key= len, reverse = True)[0]      
        while '@' in date: 
            date.remove('@')

        date, error = check_string(date)
        
        print(date + ' --- ' + str(error))
        df = df.append({'Date_ID': ID, 'registration': date,'error': error}, ignore_index=True)
    else:
        df = df.append({'Date_ID': ID, 'registration': '','error': 1}, ignore_index=True)
    return df
    

df = pd.DataFrame(columns = ['Date_ID', 'registration', 'error'])         
for i in range(0,294):
    print(i)
    df = detect_text(f'./../dataset_particulars/dates/test/{i}.png',i, df)
print(df)    
df.to_csv('./../results/google_results_date.csv', index= False)