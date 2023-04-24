import flask
from flask import Flask, render_template, request, session
from database import DBmanager, credentials
import flask_login
from flask_login import current_user
import random
app = Flask(__name__)
creds = credentials('database/credentials.json')
db = DBmanager(creds)
app.secret_key = 'some secret key'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
def getuser():
    if not current_user.is_authenticated:
        return {
            'name': 'na',
            'logged_in': False
        }
    else:
        return {
            'name': current_user.name,
            'logged_in': True

        }
import login






@flask_login.login_required
@app.route("/vote")
def vote():
    return 'pass'



@app.route("/view_debate")
def view_debate(msg='', id=''):
    id = request.args.get('id', id)
    debate = db.get_multirow_structure(id, 'debate')
    print(debate)
    title = debate[0]['title']
    # 1. Get list of nodes
    nodes = db.get_nodes(id)
    # 2. Get list of edges
    edges = db.get_edges(id)
    # 3. Get list of votes
    votes = db.get_votes(id)


    return render_template("view_debate.html",msg=msg, debate_id=id, user=getuser(), title=title, nodes=nodes, edges=edges, votes=votes)

@flask_login.login_required
@app.route("/add_connection", methods=['POST', 'GET'])
def add_connection():
    to = request.form['connectionto']
    fr = request.form['connectionfrom']
    type = request.form['connectiontype']
    id = request.form['debate_id']

    if to == fr:
        return view_debate(msg="Source and destination premises must be distinct", id=id)

    db.add_edge([{
         'debate_id': id,
        'edge_id': random.randint(0, 2147483647), # FIXME
        'source_node': fr,
        'dest_node': to,
        'types': type
    }])

    return view_debate(msg="Connection Added", id=id)

@flask_login.login_required
@app.route('/create_debate', methods=['POST', 'GET'])
def add_debate():
    if flask.request.method == 'POST':
        new_debate_id =random.randint(0, 2147483647) # FIXME
        db.add_multirow_structure('debate', [{
          'debate_id': new_debate_id,
          'title': request.form['title']
        }])
        return view_debate(msg = 'Debate created sucessfully', id=new_debate_id)
    else:
        return render_template('start_new.html', user=getuser())


@flask_login.login_required
@app.route("/delete_node", methods=['POST', 'GET'])
def delete_node():
    # Delete a node with the given ID. Admin only (for now)
    node_id = request.form['delete_node']
    debate_id = request.form['debate_id']
    db.delete_node(debate_id, node_id)
    return view_debate(id=debate_id, msg='Node deleted successfuly.')

@flask_login.login_required
@app.route("/delete_edge", methods=['POST', 'GET'])
def delete_edge():
    # Delete a node with the given ID. Admin only (for now)
    node_id = request.form['delete_edge']
    debate_id = request.form['debate_id']
    db.delete_edge(debate_id, node_id)
    return view_debate(id=debate_id, msg='Edge deleted successfuly.')
@flask_login.login_required
@app.route("/add_premise", methods=['POST', 'GET'])
def add_premise():
    contents = request.form['premise']
    debate_id = request.form['debate_id']
    type = 'premise'
    node_id = random.randint(0, 2147483647) # FIXME
    db.add_node([{
        'debate_id': debate_id,
        'node_id': node_id,
        'type': type,
        'contents': contents
    }])
    return view_debate(msg='premise added successfully', id=debate_id)
@app.route('/')
def homepage():

    user = getuser()
    return render_template("homepage.html", user=user, debate_list = db.get_debate_list(), )


if __name__ == '__main__':
    app.run(host="0.0.0.0")
