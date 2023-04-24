from flask import Flask, render_template, request
from database import DBmanager, credentials
app = Flask(__name__)

creds = credentials('database/credentials.json')
db = DBmanager(creds)



@app.route("/view_debate")
def view_debate():
    id = request.args.get('id')
    # 1. Get list of nodes
    nodes = db.get_nodes(id)
    # 2. Get list of edges
    edges = db.get_edges(id)
    # 3. Get list of votes
    votes = db.get_votes(id)


    return render_template("view_debate.html", nodes=nodes, edges=edges, votes=votes)



@app.route('/')
def homepage():
    return render_template("homepage.html", debate_list = db.get_debate_list())


if __name__ == '__main__':
    app.run(host="0.0.0.0")
