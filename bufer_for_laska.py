from flask import Flask, request, send_file
import requests
import os
import json

from aiohttp.client import ClientSession
import asyncio
import base64

async def api_call():
    async with ClientSession() as session:
        lang = 'RU'
        image_bytes = open('file_name.jpg', 'rb')
        url = 'https://scanface.soulsolutions.tech/image-api'
        try:
            params = {'lang': lang}
            data = {'image': image_bytes}
            async with session.post(url, params=params, data=data) as response:
                if response.status != 200:
                    return cls._raise_error('Error {}: {}'.format(response.status, await response.text()),
                                            on_error=on_error)
                else:
                    result_object = await response.json()
        except ClientError as e:
            logger.error(traceback.format_exc())
            return await cls._raise_error(str(e), on_error=on_error)

    if not result_object['success']:
        error = result_object.get('error', 'Scanface Image API error')
        return await cls._raise_error(error, on_error=on_error)

    
    return result_object

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home_page():
    return 'home page'

@app.route('/download', methods=['GET'])
def download():
    user_id = request.args.get('user_id')
    message_id = request.args.get('message_id')
    filename = user_id+'_'+message_id+'.jpg'
        
    try:
        image = open(filename, 'rb')
        return send_file(image, mimetype='image/jpeg', download_name= filename, as_attachment=True)
    except:
        return '404'

@app.route('/upload', methods=['POST'])
def upload():
    
    data = request.get_json()

    file_url = data['file_url']
    user_id = data['user_id']
    message_id = data['message_id']
    
    try:
        for file in os.listdir():
            if file[-4:] =='.jpg':
                os.remove(file)
    except:
        pass

    response = requests.get(file_url)
    
    with open('file_name.jpg', 'wb') as f:
        f.write(response.content)   

    try:
        result_object = asyncio.run(api_call())
        result_image_base64 = result_object['result']['images'][0]
        result_image_bytes = base64.decodebytes(result_image_base64[23:].encode())
        #image_name = result_object['result']['image_name']
        #targets = result_object['result']['predictions']
            
        with open(user_id+'_'+message_id+'.jpg', 'wb') as f:
            f.write(result_image_bytes)
      
        return result_object
    
    except:
        return 'no succsess'
    
     

if __name__ == '__main__':
    app.run(port=7777)

