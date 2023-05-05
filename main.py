import json

import flask
from flask import Flask, render_template, request, session
from database import DBmanager, credentials
import flask_login
from flask_login import current_user
import random
import openai
openai.api_key = "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"
app = Flask(__name__)
creds = credentials("database/credentials.json")
db = DBmanager(creds)
app.secret_key = "some secret key"
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
def getuser():
    if not current_user.is_authenticated:
        return {
            "name": "na",
            "logged_in": False
        }
    else:
        return {
            "name": current_user.name,
            "logged_in": True

        }
import login







@flask_login.login_required
@app.route("/vote")
def vote():
    return "pass"

def ai_moderate(original, update):
    prompt = """
    You are a moderator checking for edits in a debate website. Our website allows users to modify nodes to correct typos, improve phrasing, or clarify their reasoning. What we want to avoid is users defacing a node in a malicious context. You are to serve as a moderator of this content. You will be provided with two strings: "original" and "updated". If the "updated" string is within the spirit of the original, reply "accept". If the updated strays too far, reply "reject" and state your reason for rejecting. If you reject the update because it is logically inconsistent with the original, you can suggest the user adds a new premise rather than attempting to update it (the comment will be shown directly to the user). No matter what, do not make statements about whether the update is factually correct or not.
    Reply in JSON format using the following structure
    {"verdict": accept | reject
     "comment": if there is a comment include it here. You don"t always have to comment. If it"s  accept, then no comment is needed.}

    original: """ + original + f"""
    updated: {update}
    """
    print(prompt)
    response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0.3, max_tokens=300)
    data = json.loads(response["choices"][0]["text"])
    return data
def ai_infer(debate_id, topic):
    # Make a request to openAI to automatically populate with some nodes

    prompt = """
    debatex is a debate platform where controversial societal topics are debated. The structure of the debate is a graph, where nodes represent "premises", and edges represent connections between premises (such as support, conflict, or refutation. ) Also included is an orientation value from 0 to 100. Nodes representing conflicting viewpoints should be oriented towards polarized orientation values.
    Below is an example of the nodes and edges for a debate titled "should abortion be legal?.
    {"nodes": [
            { "id":1489031941, "label": "Abortion should be legal", "orientation": 100},
            { "id": 1777467797, "label": "Abortion should be illegal", "orientation": 0},
            { "id": 339673805, "label": "Abortion is not immoral", "orientation": 75},
            { "id": 1290090439, "label": "Unborn fetuses do not have the capacity for emotions, or human consciousness, so an abortion is not morally questionable", "orientation": 75},
            { "id": 1862081395, "label": "Persons have a right to life, and it is immoral to kill a being with a right to life, and the embryo or fetus is a person. It follows that it is immoral to kill an unborn fetus.", "orientation": 25},
            { "id": 2107962273, "label": "Abortion is immoral", "orientation": 0},
            { "id": 110041032, "label": "Mothers suffering from unwanted pregnancies due to rape or abuse should not be forced to carry the child", "orientation": 100},
            { "id": 614409854, "label": "Access to abortion is a human right", "orientation": 100},
            { "id": 912745007, "label": "The embryo or fetus is not a person", "orientation": 75},
            { "id": 864973073, "label": "Only persons have the capacity for human emotions and consciousness", "orientation": 75},
            { "id": 572859830, "label": "It is exclusively the mother"s decision to determine whether to abort the fetus", "orientation": 100},
            { "id": 1446383747, "label": "Abortion restrictions do not prevent abortions from happening, because people will still do home abortions in a less safe and sanitary way", "orientation": 100},
            { "id": 1309807795, "label": "Access to abortion is not a human right", "orientation": 25},
            { "id": 303254331, "label": "Persons have a right to life", "orientation": 25},
            { "id": 779854297, "label": "It is wrong to kill a being with a right to life", "orientation": 25},
            { "id": 116382449, "label": "It is impossible to prove whether fetuses are capable of experiencing human consciousness or emotions", "orientation": 75},
            { "id": 1907427755, "label": "The embryo or fetus is a person", "orientation": 25},
            { "id": 784168977, "label": "Right to life is a human right, all persons are entitled to human rights, and embryos or fetuses are persons. Therefore, aborting a fetus is to deprive a person of a human right. Therefore, abortion is not a human right", "orientation": 0},
            { "id": 683183832, "label": "Right to life is a human right", "orientation": 25},
            { "id": 366355334, "label": "Freedom from torture is a human right", "orientation": 100},
            { "id": 726852648, "label": "Being forced to carry the child of a rape or abuse is considered torture", "orientation": 100},
            { "id": 1584788096, "label": "Freedom from torture is a human right, and being forced to carry the child of a rape may be considered torture. Therefore the ability to abort the fetus is the only way to be free from torture in this situation, and access to an abortion is critical to ensuring the human rights of the mother.", "Orientation": 95}
          ],
    "edges": [
    {
    "from": 1489031941,
    "to": 1777467797,
    "label": "contradict",
    "id": 170976863
    },
    {
    "from": 1489031941,
    "to": 339673805,
    "label": "support",
    "id": 1931471513
    },
    {
    "from": 339673805,
    "to": 1290090439,
    "label": "support",
    "id": 237311465
    },
    {
    "from": 339673805,
    "to": 2107962273,
    "label": "contradict",
    "id": 786328402
    },
    {
    "from": 1777467797,
    "to": 2107962273,
    "label": "support",
    "id": 762861575
    },
    {
    "from": 2107962273,
    "to": 1862081395,
    "label": "support",
    "id": 132380000
    },
    {
    "from": 1489031941,
    "to": 1446383747,
    "label": "support",
    "id": 514284951
    },
    {
    "from": 1489031941,
    "to": 572859830,
    "label": "support",
    "id": 1086402462
    },
    {
    "from": 1290090439,
    "to": 864973073,
    "label": "support",
    "id": 1466568004
    },
    {
    "from": 1489031941,
    "to": 614409854,
    "label": "support",
    "id": 1398589763
    },
    {
    "from": 1290090439,
    "to": 912745007,
    "label": "support",
    "id": 1005732506
    },
    {
    "from": 614409854,
    "to": 110041032,
    "label": "support",
    "id": 1328909052
    },
    {
    "from": 1777467797,
    "to": 1309807795,
    "label": "support",
    "id": 172974565
    }]
    
    You are to act as a high IQ, intellectual college professor from a top university. Your task is to create a new similarly structured JSON with nodes and edges for a new debate titled""" +  f""" "{topic}". Your response must be properly JSON formated. Try to have an equal number of supporting and contradicting viewpoints. Each node and edge MUST have a unique identifier between 1 and 2147483647. Limit yourself to less than 10 nodes and 20 total edges. Absolutely do not include anything in your response except for the JSON object. """
    response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0.1, max_tokens=2000)
    print(response["choices"][0]["text"])
    data = json.loads(response["choices"][0]["text"])
    for x in data["nodes"]:
        # Add to database

        db.add_node([{
            "debate_id": debate_id,
            "node_id": x["id"],
            "type": "premise",
            "contents": x["label"]
        }])

        db.update_color_vote(
            debate_id,
            x["id"],
            x["orientation"],
            "ai_mod"
        )

    for x in data["edges"]:
        # Add to database
        db.add_edge([{
            "debate_id": debate_id,
            "edge_id": x["id"],  # FIXME
            "source_node": x["from"],
            "dest_node": x["to"],
            "types": x["label"]
        }])






@app.route("/view_debate")
def view_debate(msg="", id=""):
    id = int(request.args.get("id", id, int))
    debate = db.get_multirow_structure(id, "debate")
    db.add_view(id)
    print(debate)
    title = debate[0]["title"]
    # 1. Get list of nodes
    nodes = db.get_nodes(id)
    # 2. Get list of edges
    edges = db.get_edges(id)
    # 3. Get list of votes
    votes = db.get_votes(id)

    colors = db.get_colors(id)
    user_votes = db.get_user_vote(id, getuser()["name"])

    for x in edges:
        if int(x["id"]) not in votes["edge"].keys():
            votes["edge"][x["id"]] = {
                "likes": 0,
                "dislikes": 0,
                "ratio": None
            }

        x["likes"] = votes["edge"][x["id"]]["likes"]
        x["dislike"] = votes["edge"][x["id"]]["dislikes"]
        x["ratio"] = votes["edge"][x["id"]]["ratio"]

    for x in nodes:
        if int(x["id"]) not in votes["node"].keys():
            votes["node"][x["id"]] = {
                "likes": 0,
                "dislikes": 0,
                "ratio": None
            }

        x["likes"] = votes["node"][x["id"]]["likes"]
        x["dislike"] = votes["node"][x["id"]]["dislikes"]
        x["ratio"] = votes["node"][x["id"]]["ratio"]
        x['id'] = int(x['id'])
        if int(x['id']) not in colors.keys():
            colors[int(x['id'])] = {}

            colors[int(x['id'])]['hex'] = '#FFFFFF'
            colors[x['id']]['int'] = '50'

        x['color'] = colors[x['id']]['hex']
        x['color_int'] = colors[x['id']]['int']





    return render_template("view_debate.html",msg=msg, debate_id=id, user=getuser(), title=title, nodes=nodes, edges=edges, votes=votes, user_votes=user_votes)

@flask_login.login_required
@app.route("/add_connection", methods=["POST", "GET"])
def add_connection():
    to = request.form["connectionto"]
    fr = request.form["connectionfrom"]
    type = request.form["connectiontype"]
    id = request.form["debate_id"]

    if to == fr:
        return view_debate(msg="Source and destination premises must be distinct", id=id)

    db.add_edge([{
         "debate_id": id,
        "edge_id": random.randint(0, 2147483647), # FIXME
        "source_node": fr,
        "dest_node": to,
        "types": type
    }])

    return view_debate(msg="Connection Added", id=id)

@flask_login.login_required
@app.route("/create_debate", methods=["POST", "GET"])
def add_debate():
    if flask.request.method == "POST":
        new_debate_id =random.randint(0, 2147483647) # FIXME
        ai_infer(new_debate_id, request.form["title"])

        db.add_multirow_structure("debate", [{
          "debate_id": new_debate_id,
          "title": request.form["title"],
          "views": 0,
        }])

        return view_debate(msg = "Debate created sucessfully", id=new_debate_id)
    else:
        return render_template("start_new.html", user=getuser())


@flask_login.login_required
@app.route("/delete_node", methods=["POST", "GET"])
def delete_node():
    # Delete a node with the given ID. Admin only (for now)
    node_id = request.form["delete_node"]
    debate_id = request.form["debate_id"]
    db.delete_node(debate_id, node_id)
    return view_debate(id=debate_id, msg="Node deleted successfuly.")

@flask_login.login_required
@app.route("/delete_edge", methods=["POST", "GET"])
def delete_edge():
    # Delete a node with the given ID. Admin only (for now)
    node_id = request.form["delete_edge"]
    debate_id = request.form["debate_id"]
    db.delete_edge(debate_id, node_id)
    return view_debate(id=debate_id, msg="Edge deleted successfuly.")

@flask_login.login_required
@app.route("/edit_premise",  methods=["POST", "GET"])
def update_premise():
    original = request.args.get("original")
    update = request.args.get("update")
    node_id = request.args.get("node_id")
    debate_id = request.args.get("debate_id")
    moderation_verdict = ai_moderate(original, update)
    print(moderation_verdict)
    if moderation_verdict["verdict"] == "accept":
        user_id = getuser()["name"]

        db.update_node(debate_id, node_id, update, user_id, original)
        # Update node in the database
        # accept
    return moderation_verdict

@flask_login.login_required
@app.route("/add_premise", methods=["POST", "GET"])
def add_premise():
    contents = request.form["premise"]
    debate_id = request.form["debate_id"]
    type = "premise"
    node_id = random.randint(0, 2147483647) # FIXME
    db.add_node([{
        "debate_id": debate_id,
        "node_id": node_id,
        "type": type,
        "contents": contents
    }])
    return view_debate(msg="premise added successfully", id=debate_id)

@flask_login.login_required
@app.route("/submit_vote")
def submit_vote():
    debate_id = request.args.get("debate_id", -1, type=int)

    object_type = request.args.get("object_type", -1, type=str)
    assert object_type in ["node", "edge"]

    object_id = request.args.get("object_id", -1, type=int)

    vote = request.args.get("vote", 0, type=int) # 0 for downvote. 1 for upvote
    assert vote in [1, -1]

    user_id = getuser()["name"]
    print((debate_id, object_type, object_id, vote, user_id))
    db.update_vote(debate_id, object_type, object_id, vote, user_id)
    return "success"


@flask_login.login_required
@app.route('/vote_color')
def vote_color():
    debate_id = request.args.get("debate_id", -1, type=int)

    node_id = request.args.get("node_id", -1, type=int)

    value = request.args.get("value", 0, type=int) # 0 for downvote. 1 for upvote
    assert value in range(0, 101)

    user_id = getuser()["name"]
    db.update_color_vote(debate_id, node_id, value, user_id)

    # Get new updated color

    new_hex = db.get_color_specific(debate_id, node_id)


    return {'new_hex': new_hex}


@app.route("/")
def homepage():

    user = getuser()
    return render_template("homepage.html", user=user, debate_list = db.get_debate_list(), )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
