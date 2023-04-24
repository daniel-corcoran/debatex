import psycopg2
import json
import time
import ast
import random
import hashlib

schema = {
    "debate": [
        "debate_id",
        "title"
    ],
    "node": [
        "debate_id",
        "node_id", # UUID
        "type", # premise or data
        "contents"
    ],
    "edge": [
        "debate_id",
        "edge_id",
        "source_node", # UUID
        "dest_node", # UUID
        "types" # Support, contradiction
    ],
    "edit": [ # Edit history
        'debate_id',
        'edit_id',
        'user_id',
        'timestamp',
        'object_type', # Editing a node or edge?
        'contents_before',
        'contents_after'
    ],
    "users": [
        'user_id',
        'user_name',
        'pass_hash',
        'last_login'
    ],
    "vote": [
        'debate_id',
        'node_id',
        'user_id',
        'timestamp',
        'vote'

    ]




}

class credentials:
    def __init__(self, json_path):
        with open(json_path) as f:
            cred_dic = json.load(f)
            self.host = cred_dic['host']
            self.database = cred_dic['database']
            self.user = cred_dic['user']
            self.port = cred_dic['port']
            self.password = cred_dic['password']


class DBmanager:

    def reconnect(self, creds):
        start = time.time()
        self.conn = psycopg2.connect(
            database=creds.database,
            user=creds.user,
            password=creds.password,
            host=creds.host,
            port=creds.port)
        end = time.time()

    def get_db(self):

        self.reconnect(self.creds)

        return self.conn

    def escape_string(self, value):
        if isinstance(value, str):
            if "'" in value:
                return str(value.replace("'", "''"))
            else:
                return value
        else:
            return value

    def add_multirow_structure(self, table, multirow_struct):
        # Description: Adds a multirow structure to the table
        # @table - name of the table we are adding data to
        # @multirow-struc - a list of dictionaries to be appended to the database.
        # The dic keys must match the DB schema.

        db = self.get_db()
        cur = db.cursor()

        for struct in multirow_struct:
            assert list(struct.keys()) == schema[table], "structure most conform to the predefined schema"

            for x in struct:
                if type(struct[x]) == str:
                    struct[x] = f"'{self.escape_string(struct[x])}'"
            # FIXME: This could be vulnerable to SQL injection. Can we rewrite this to not do string formatting?
            cur.execute(f"""INSERT INTO {table}
                            ({", ".join(schema[table])})
                            VALUES ({", ".join(str(struct[i]) for i in schema[table])})""")
        self.conn.commit()
        cur.close()

    def get_multirow_structure(self, debate_id, table):
        try:
            db = self.get_db()
            cur = db.cursor()
            cur.execute(f"""SELECT * 
                               FROM {table}
                               WHERE debate_id = {int(debate_id)}""")
            rows = cur.fetchall()
            self.conn.commit()
            cur.close()
            return_struc = []
            for row in rows:
                data_struc = {}
                for index, i in enumerate(schema[table]):
                    data_struc[i] = row[index]
                return_struc.append(data_struc)
            return return_struc
        except psycopg2.DatabaseError as error:
            print(error)



    def generateNewUniqueUserID(self):
        # This function generates a random survey ID between 10000 and 99999
        # Guaranteed not to collide with any preexisting survey ids.

        solved = False
        while not solved:
            new_id = random.randint(0, 2147483647)

            if not self.check_user_id(new_id):  # Meaning there is no survey that has this ID
                solved = True

        return new_id

    def check_user(self, id):
        # Checks if a username exist
        try:
            db = self.get_db()
            cur = db.cursor()
            cur.execute(f"""SELECT * 
                               FROM users
                               WHERE user_name = %s""", [id])
            rows = cur.fetchall()
            self.conn.commit()
            cur.close()
            if len(rows):
                print("User exists in DB")
                return True
            else:
                print("User doesn't exist in DB")
                return False
        except psycopg2.DatabaseError as error:
            print(error)

    def check_user_id(self, id):
        # Checks if a userID exist
        try:
            db = self.get_db()
            cur = db.cursor()
            cur.execute(f"""SELECT * 
                               FROM users
                               WHERE user_id = %s""", [id])
            rows = cur.fetchall()
            self.conn.commit()
            cur.close()
            if len(rows):
                print("User exists in DB")

                return True
            else:
                print("User doesn't exist in DB")
                return False
        except psycopg2.DatabaseError as error:
            print(error)

    def authenticate_user(self, password='', username=''):
        try:
            db = self.get_db()
            cur = db.cursor()
            cur.execute(f"""SELECT * 
                               FROM users
                               WHERE user_name = %s""", [username])
            rows = cur.fetchall()
            self.conn.commit()
            cur.close()
            if len(rows):
                if str(hashlib.sha256(password.encode()).hexdigest()) == rows[0][2]:
                    return True
                else:
                    print("Incorrect password match")
                    return False
            else:
                print("User doesn't exist in DB")
                return False
        except psycopg2.DatabaseError as error:
            print(error)

        return username == 'user' and password == 'pass' # FIXME

    def get_nodes(self, id):
        nodes = self.get_multirow_structure(id, 'node')
        new_struc = []
        for x in nodes:
            new_struc.append({
                'id': x['node_id'],
                'type': x['type'],
                'label': x['contents']

            })
        return new_struc

    def add_node(self, struc):
        self.add_multirow_structure('node', struc)

    def get_edges(self, id):
        nodes = self.get_multirow_structure(id, 'edge')
        new_struc = []
        for x in nodes:
            if x['types'] == 'support':
                arrow = 'from'
                color = "{ color: 'blue' }"
                label = "supports"
            if x['types'] == 'refute':
                color = "{ color: '#8B8000' }"

                arrow = 'from'
                label = "refutes"
            if x['types'] == 'contradict':
                color = "{ color: 'red' }"
                label = "contradicts"
                arrow = "to, from"
            new_struc.append({
                'to': x["dest_node"],
                'from': x["source_node"],
                'arrow': arrow,
                'color': color,
                'label': label,
                'id': x['edge_id']
            })
        return new_struc
    def add_edge(self, struc):
        self.add_multirow_structure('edge', struc)


    def get_votes(self, id):
        return None


    def delete_node(self, debate_id, node_id):
        try:
            db = self.get_db()
            cur = db.cursor()
            cur.execute(f"""DELETE
                               FROM node
                               WHERE debate_id = %s and node_id = %s""", [debate_id, node_id])
            self.conn.commit()
            cur.close()
        except psycopg2.DatabaseError as error:
            print(error)
    def delete_edge(self, debate_id, edge_id):
        try:
            db = self.get_db()
            cur = db.cursor()
            cur.execute(f"""DELETE
                               FROM edge
                               WHERE debate_id = %s and edge_id = %s""", [debate_id, edge_id])
            self.conn.commit()
            cur.close()
        except psycopg2.DatabaseError as error:
            print(error)
    def get_debate_list(self):
        db = self.get_db()
        cur = db.cursor()
        cur.execute(f"""SELECT * 
                           FROM debate""")
        rows = cur.fetchall()
        self.conn.commit()
        cur.close()
        print(rows)
        new_struc = []
        for x in rows:
            new_struc.append({
                'debate_id': x[0],
                'title': x[1]
            })
        return new_struc

    def __init__(self,
                 creds):
        print("Establishing connection to database....")
        self.conn = psycopg2.connect(
            database=creds.database,
            user=creds.user,
            password=creds.password,
            host=creds.host,
            port=creds.port)
        self.creds = creds
        print(f"Connected to database at {creds.host}")