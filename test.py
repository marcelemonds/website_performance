import json
import requests
import urllib
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# google documentation for further reading
# https://developers.google.com/speed/docs/insights/v5/get-started


# relevant audits for each category
audits = {
    'performance': [
        'interactive',
        'largest-contentful-paint',
        'speed-index',
        'total-blocking-time',
        'cumulative-layout-shift',
        'first-contentful-paint'
    ],
    'seo': [
        'plugins',
        'link-text',
        'http-status-code',
        'robots-txt',
        'document-title',
        'font-size',
        'viewport',
        'meta-description',
        'structured-data',
        'tap-targets',
        'hreflang',
        'canonical',
        'image-alt',
        'crawlable-anchors'
    ],
    'accessibility': [],
    'best-practices': [],
    'pwa': []
}


def get_config():
    load_dotenv()

    url = os.environ.get('URL')
    language = os.environ.get('API_LANGUAGE')
    key = os.environ.get('API_KEY')
    strategy = os.environ.get('API_STRATEGY')
    category = os.environ.get('API_CATEGORY')
    csv_export = os.environ.get('CSV_EXPORT')

    return url, language, key, strategy, category, csv_export


def api_call(url, language, key, strategy, category):
    try:
        api_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?locale={language}&url={url}&key={key}&strategy={strategy}&category={category}'
        result_raw = urllib.request.urlopen(api_url).read().decode('UTF-8')
        result_raw_json = json.loads(result_raw)
        return result_raw_json
    except Exception as e:
        print(e)
        return {'api_call_error': e}


def result_to_csv(result):
    today = datetime.today().strftime('%Y%m%d')
    filename = f'{today}_{result["type"]}_{result["device"]}.csv'
    with open(filename, 'w', newline='') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key, value in result.items():
            if key == 'audits':
                for item in value:
                    csv_writer.writerow(item)
            else:
                csv_writer.writerow([key, value, ''])


def performance_data(url, language, key, strategy, category, csv_export=False):
    result_raw_json = api_call(url, language, key, strategy, category)

    result = {
        'url': url,
        'type': category,
        'device': strategy,
        'error': None,
        'score': '',
        'audits': []
    }

    if 'api_call_error' in result_raw_json:
        result['error'] = result_raw_json['api_call_error']
    else:
        score = int(result_raw_json['lighthouseResult']['categories'][category]['score'] * 100)
        result['score'] = score

        for audit in audits[category]:
            audit_raw = result_raw_json['lighthouseResult']['audits'][audit]
            title = audit_raw['title']
            description = audit_raw['description'].replace('[Weitere Informationen.]', '').replace('[Weitere Informationen]', '')

            audit_data = [title, '', description]
            if 'displayValue' in audit_raw:
                value = audit_raw['displayValue']
                audit_data[1] = value
            result['audits'].append(audit_data)

    if csv_export:
        result_to_csv(result)

    return result


if __name__ == '__main__':
    url, language, key, strategy, category, csv_export = get_config()
    performance_data(url, language, key, strategy, category, csv_export)
