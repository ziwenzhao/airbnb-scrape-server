from flask import Flask
from flask import request
from flask import abort
from flask import Response
from flask import jsonify
print('applcaiton.py started')
from time import sleep
import os
import subprocess
import uuid
import logging
from exception_model import InvalidUsage
from maintain_files import clean_files_periodically


application = Flask(__name__)

application.logger.setLevel(logging.INFO)

clean_files_periodically(application)

@application.route('/scrape_homes', methods = ['post'])
def scrape_homes():
    
    if request.form.get('url') is None or request.form.get('max_page_number') is None:
        raise InvalidUsage(message='request body missed parameters. The paramters of url and max_page_number are required',\
                           status_code=422, payload={'url': '/scrape_homes', 'method': 'post'})
    job_id = uuid.uuid1()
    try:
        application.logger.info('start scrape homes')
        subprocess.check_output('cd ./airbnb\ homes\ scrape && scrapy crawl home -a url="' + request.form.get('url') + '" -a max_page_number=' \
                        + request.form.get('max_page_number') + ' -t json -o -> home_' + str(job_id) + '.json', shell=True)
        application.logger.info('scrape homes done')
        return {'job_id': job_id}
    except Exception as e:
        application.logger.error('scrape homes error: ' + str(e))
        raise InvalidUsage(message=str(e), status_code=500)



@application.route('/get_homes', methods=['get'])
def get_homes():
    job_id = request.args.get('job_id') 
    if job_id is None:
        raise InvalidUsage(message='request missed query parameters. The paramters of job_id is necessary',\
                           status_code=422, payload={'url': '/get_homes', 'method':'get'})
    try:
        application.logger.info('open file: ./airbnb homes scrape/home_' + job_id + '.json')
        with open('./airbnb homes scrape/home_' + job_id + '.json' ) as file:
            return file.read()
    except Exception as e:
        application.logger.error('file: ./airbnb homes scrape/home_' + job_id + '.json open failed: ' + str(e))
        raise InvalidUsage(message=str(e), status_code=404)




@application.route('/delete_file', methods=['delete'])
def delete_file():
    job_id = request.args.get('job_id')
    if job_id is None:
        raise InvalidUsage(message='request missed query parameters. The paramters of job_id is necessary',\
                           status_code=422, payload={'url': '/delete_file', 'method':'delete'})
    file_path = './airbnb homes scrape/home_' + job_id + '.json'
    if os.path.exists(file_path):
        application.logger.info('file exists, will be removed')
        os.remove(file_path)
        application.logger.info('file removed')
        return 'File removed.'
    else:
        application.logger.info('file does not exist')
        return 'file does not exist'



@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logging_dict = error.to_dict()
    logging_dict['status_code'] = error.status_code
    application.logger.error(logging_dict)
    return response


if __name__ == "__main__":
    application.run()
