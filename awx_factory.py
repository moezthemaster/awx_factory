import json
import os
import requests
import sys
import urllib3
import warnings
from time import sleep

sys.path.append('./settings')
import config

RUN_STATUS = ['successful', 'failed']
AWX_USERNAME = config.AWX_CONFIG['awx_username']
AWX_PASSWORD = config.AWX_CONFIG['awx_password']


def request_method(action):
    """

    :param action: takes create or delete
    :return: headers and base url to request method
    """

    headers = {"Content-type": "application/json", "Accept": "application/json"}
    if action == 'launch':
        url = config.AWX_CONFIG['awx_base_url'] + "/job_templates/{}/launch/"
    elif action == 'check_job_status':
        url = config.AWX_CONFIG['awx_base_url'] + "/jobs/{}"
    return headers, url


def submit_request(launch_job_url, headers, username, password):
    """

    :param launch_job_url:
    :param headers:
    :param username:
    :param password:
    :return:
    """
    warnings.simplefilter('ignore', urllib3.exceptions.SecurityWarning)
    try:
        r = requests.post(url=launch_job_url, verify=False, headers=headers, auth=(username, password))
    except Exception:
        raise
    return r.json()


def build(job_template_id):
    """

    :param job_template_id: job template id to launch(create or delete)
    :return:
    """

    try:
        request_parameters = request_method('launch')
        url = request_parameters[1].format(job_template_id)
        headers = request_parameters[0]
    except Exception:
        raise
    try:
        run = submit_request(url, headers, username=AWX_USERNAME, password=AWX_PASSWORD)
        job_id = run['job']
    except Exception:
        raise

    job_status = ''
    count = 0

    while job_status not in RUN_STATUS and count < 90:
        try:
            sleep(30)
            request_parameters = request_method('check_job_status')
            url = request_parameters[1].format(job_id)
            run = submit_request(url, headers, username=AWX_USERNAME, password=AWX_PASSWORD)
            job_status = run['status']
            count += 1
        except Exception:
            raise

    if job_status == 'successful':
        result = {"status": job_status, "job_id": job_id}
    elif job_status == 'failed':
        result = {"status": job_status, "job_id": job_id}
    return result


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'install':
            job_template_id = config.AWX_CONFIG['job_template_install_nginx']
        elif sys.argv[1] == 'uninstall':
            job_template_id = config.AWX_CONFIG['job_template_uninstall_nginx']
    except Exception:
        raise
    run_build = build(job_template_id)
    print("{}".format(json.dumps(run_build)))
