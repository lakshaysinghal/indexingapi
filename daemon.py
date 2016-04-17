from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import redis
from datetime import datetime
from flask.ext.cors import CORS
app = Flask(__name__)
CORS(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
es = Elasticsearch()


@app.route('/index/', methods=['POST', 'GET'])
def index():
	if request.method == 'GET':
		query = request.args.get("q")
		try:
			res = redis_client.get(query)
			return jsonify({query:res})
		except:
			return "Name does not exist!"

	if request.method == 'POST':
		author = request.values.get("author")
		msg = request.values.get("msg")
		doc = {
			"author":author,
			"text":msg,
			"timestamp":datetime.now()
		}
		try:
			es.index(index="test-index", doc_type='messages', body=doc)
			redis_client.set(author, msg)
			return "Indexed successfully"
		except :
			return "Caught an error! Please try again!"


@app.route('/search/', methods=['GET'])
def search():
	query = request.args.get('q')
	try:
		res = es.search(index="test-index", body={"query": {"term": {'author':query}}})
		data = []
		for hit in res['hits']['hits']:
			data.append({'author':str(hit['_source']["author"]), 'msg':hit['_source']["text"]})
		return jsonify(data=data)
	except:
		return "Name does not exist!"


if __name__ == '__main__':
  app.run( 
        host="0.0.0.0",
        port=int("5000")
  )
