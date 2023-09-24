import os
import KEY
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY.GOOGLE_API_KEY

def detect_document(path):
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    print(response.full_text_annotation.text)

    return response.full_text_annotation.text

    #print(response.full_text_annotation)
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

if __name__ == '__main__':
    img ='sample.jpg'   
    detect_document(img)