from flask import Flask, render_template, request, json
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.debug = True
client = Elasticsearch()
ES_BUG_INDEX = "bugdb"

tags_dict = {"ASSIGNED_TO": "PROGRAMMER", "COMPONENT": "CATEGORY", "STATUS": "STATUS", "RPTD_BY": "RPTD_BY"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def api_search():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json

        return json.dumps(getNItems(data))
    return "No Data"


@app.route('/searchAll', methods=['POST'])
def api_search_all():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json
        # print(data)
        return json.dumps(getMatchingBugs(data))
    return "No Data"


@app.route('/suggest')
def api_suggest():
    # print("here")
    if 'query' in request.args:
        # print(request.args['query'])
        return json.dumps(getSuggestItems(request.args['query']))
    else:
        return 'Nothing to Query'


@app.route('/bug/<bugid>')
def api_bug(bugid):
    # print(bugid)
    response = client.get(index=ES_BUG_INDEX, doc_type='bugdb', id=bugid)
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


def getMatchingBugs(data):
    response = ""
    filter = []
    query = {"size": 50, "_source": ["SUBJECT", "RPTNO"], "query": {"bool": {}},
             "highlight": {"pre_tags": ["<b>"], "post_tags": ["</b>"],
                           "fields": {"SUBJECT.simple": {}, "COMMENTS.MESSAGE": {}}}}

    filter = getFilters(data)

    should_clause =[{
               "match":{
                  "SUBJECT.simple":{
                     "query":data["text"],
                      "operator":"and"
                  }
               }
            },
            {
               "nested":{
                  "path":"COMMENTS",
                  "score_mode":"max",
                  "query":{
                     "bool":{
                        "must":{
                           "match":{
                              "COMMENTS.MESSAGE":{
                                 "query":data["text"],
                                 "operator":"and"
                              }
                           }
                        }
                     }
                  }
               }
            }]

    if len(filter) > 0 and len(data["text"]) == 0:
        query["query"]["bool"].update({"should":{"match_all": {}}})
        query["query"]["bool"].update({"filter": filter})
    elif len(filter) > 0 and len(data["text"]) > 0:
        query["query"]["bool"].update({"should":should_clause })
        query["query"]["bool"].update({"filter": filter})
    else:
        query["query"]["bool"].update({"should": should_clause})
    response = client.search(
        index=ES_BUG_INDEX,
        body=json.dumps(query))
    print(json.dumps(query))
    return response


def getFilters(data):
    filter = []
    if len(data["tags"]) > 0:
        for obj in data["tags"]:
            tag_list = obj["text"].split(":")

            if len(filter) == 0:

                filter.append({
                    "terms": {
                        tags_dict[tag_list[0]]: [
                            tag_list[1]
                        ]
                    }
                })

            else:
                flag = False

                for item in filter:

                    if tags_dict[tag_list[0]] in item["terms"]:
                        item["terms"][tag_list[0]].append(tag_list[1])
                        flag = True
                        break
                if not flag:
                    filter.append({
                        "terms": {
                            tags_dict[tag_list[0]]: [
                                tag_list[1]
                            ]
                        }
                    })
    return filter


def getNItems(data):
    query =  {
            "_source": ["SUBJECT","RPTNO"],
            "size": 20,
            "query": {
                "bool": {
                    "must": {
                        "match": {
                            "SUBJECT": {
                                "query": data["text"],
                                "operator": "and"
                            }

                        }
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
    filter = getFilters(data)
    if len(data["tags"]) > 0:
        query["query"]["bool"].update({"filter": filter})


    response = client.search(
        index=ES_BUG_INDEX,
        body=json.dumps(query)
    )
    print(json.dumps(query))
    return response
    # for hit in response['hits']['hits']:
    #   print(hit['_score'], hit['_source']['SUBJECT'])


if __name__ == '__main__':
    app.run(host='slc12acw.us.oracle.com', port=9252)


"""   query["query"]["bool"]["must"].update({"multi_match": {"query": data["text"], "type": "best_fields",
                                                               "fields": ["COMMENTS.MESSAGE", "SUBJECT.simple"]}})
        query["query"]["bool"].update({"filter": filter})
    else:
        query["query"]["bool"]["must"].update({"multi_match": {"query": data["text"], "type": "best_fields",
                                                               "fields": ["COMMENTS.MESSAGE", "SUBJECT.simple"]}})"""