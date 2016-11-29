import ConfigParser, logging, datetime, os

from flask import Flask, render_template, request
from collections import OrderedDict

import mediacloud
import json


CONFIG_FILE = 'settings.config'
basedir = os.path.dirname(os.path.realpath(__file__))

# load the settings file
config = ConfigParser.ConfigParser()
config.read(os.path.join(basedir, 'settings.config'))

# set up logging
log_file_path = os.path.join(basedir,'logs','mcserver.log')
logging.basicConfig(filename=log_file_path,level=logging.DEBUG)
logging.info("Starting the MediaCloud example Flask app!")

# clean a mediacloud api client
mc = mediacloud.api.MediaCloud( config.get('mediacloud','api_key') )

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("search-form.html")

@app.route("/search",methods=['POST'])
def search_results():
    keywords = request.form['keywords']
    startdate = request.form['start']
    enddate = request.form['end']
    now = datetime.datetime.now()
    results = mc.sentenceCount(keywords,
        solr_filter=[mc.publish_date_query( datetime.date( int(startdate[0:4]), int(startdate[5:7]), int(startdate[8:10]) ),
                                            datetime.date( int(enddate[0:4]), int(enddate[5:7]), int(enddate[8:10])) ),
                     'media_sets_id:1' ], split = True, split_start_date = startdate, split_end_date = enddate)
    results_raw = results['split']
    del results_raw['end'], results_raw['start'], results_raw['gap']
    results_weekly = OrderedDict(sorted(results_raw.items(), key=lambda t: t[0]))
    r_dump = json.dumps([dict(date=key, name='result', value=value) for key, value in results_weekly.iteritems()])
    return render_template("search-newform.html",
        keywords=keywords, labels = map(str, results['split'].keys()), sentenceCount = r_dump )

if __name__ == "__main__":
    app.debug = True
    app.run()
