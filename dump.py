import os

import biothings, config
biothings.config_for_app(config)
from config import DATA_ARCHIVE_ROOT

import biothings.hub.dataload.dumper

class LitCovidTopicsDumper(biothings.hub.dataload.dumper.DummyDumper):
    SRC_NAME = "litcovidtopics"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SCHEDULE = "40 6 * * *"

    __metadata__ = {
        "src_meta": {
            "author":{
                "name": "Ginger Tsueng",
                "url": "https://github.com/gtsueng"
            },
            "code":{
                "branch": "main",
                "repo": "https://github.com/outbreak-info/litcovidtopics.git"
            },
            "url": "https://www.ncbi.nlm.nih.gov/research/coronavirus/ ",
            "license": "https://www.ncbi.nlm.nih.gov/home/about/policies/"
        }
    }

