from flask import Flask, render_template, request, json
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.debug = True
client = Elasticsearch()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def api_search():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json
        print(data)
        return json.dumps(getNItems(data['text']))
    return "No Data"


@app.route('/suggest')
def api_suggest():
    print("here")
    if 'query' in request.args:
        print(request.args['query'])
        return json.dumps(getSuggestItems(request.args['query']))
    else:
        return 'Nothing to Query'


@app.route('/bug/<bugid>')
def api_bug(bugid):
    # print(bugid)
    response = client.get(index="bugdb2", doc_type='bugdb', id=bugid)
    # print(response)
    return json.dumps(response["_source"])


def getSuggestItems(text):
    response = client.search(
        index="tagdb",
        body={"_source": ["_id"],
              "size": 0,
              "suggest": {
                  "tag-suggest": {
                      "prefix": text,
                      "completion": {
                          "field": "suggest",
                          "size": 10
                      }
                  }
              }
              }
    )

    return response['suggest']['tag-suggest'][0]['options']
    # for hit in response['hits']['hits']:
    #   print(hit['_score'], hit['_source']['SUBJECT'])


def getNItems(text):
    response = client.search(
        index="bugdb2",
        body={
            "_source": ["SUBJECT"],
            "size": 30,
            "query": {
                "match": {
                    "SUBJECT": {
                        "query": text,
                        "operator": "and"
                    }

                }
            },
            "highlight": {
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"],
                "fields": {
                    "SUBJECT": {}
                }
            }
        }
    )
    # print(response)
    return response
    # for hit in response['hits']['hits']:
    #   print(hit['_score'], hit['_source']['SUBJECT'])


if __name__ == '__main__':
    app.run(host='slc12acw.us.oracle.com', port=9252)
