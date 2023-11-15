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
    #print(response.full_text_annotation)
    print('========신뢰도 0.8 미만인 문자========')
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\n블럭 신뢰도: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('단락 신뢰도: {}'.format(paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('단어: {} (신뢰도: {})'.format(word_text, word.confidence))

                    for symbol in word.symbols:
                        if(symbol.confidence < 0.8):
                            print('\t{} (신뢰도: {})'.format(symbol.text, symbol.confidence))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
img ='sample.jpg'   
detect_document(img)