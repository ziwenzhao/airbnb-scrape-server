from flask import Flask
from flask import request
from flask import abort
from flask import Response
from flask import jsonify
from time import sleep
import os
import logging
import subprocess
import uuid
from exception_model import InvalidUsage

app = Flask(__name__)

logger = logging.getLogger(__name__)

@app.route('/scrape_homes', methods = ['post'])
def scrape_homes():
    logger.info('scrape_homes start')
    if request.form.get('url') is None or request.form.get('max_page_number') is None:
        raise InvalidUsage(message='request body missed parameters. The paramters of url and max_page_number are required', status_code=422)
    job_id = uuid.uuid1()
    try:
        subprocess.call('cd ./airbnb\ homes\ scrape && scrapy crawl home -a url="' + request.form.get('url') + '" -a max_page_number=' \
                        + request.form.get('max_page_number') + ' -t json -o -> home_' + str(job_id) + '.json', shell=True)
        return {'job_id': job_id}
    except Exception as e:
        raise InvalidUsage(message=str(e), status_code=500)

@app.route('/get_homes', methods=['get'])
def get_homes():
    job_id = request.args.get('job_id') 
    if job_id is None:
        raise InvalidUsage(message='request missed query parameters. The paramters of job_id is necessary', status_code=422)
    try:
        with open('./airbnb homes scrape/home_' + job_id + '.json' ) as file:
            return file.read()
    except Exception as e:
        raise InvalidUsage(message=str(e), status_code=404)

@app.route('/delete_file', methods=['delete'])
def delete_file():
    job_id = request.args.get('job_id')
    if job_id is None:
        raise InvalidUsage(message='request missed query parameters. The paramters of job_id is necessary', status_code=422)
    file_path = './airbnb homes scrape/home_' + job_id + '.json'
    if os.path.exists(file_path):
        os.remove(file_path)
        return 'File removed.'
    else:
        return 'file does not exist'
        

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


