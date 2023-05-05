import datetime

import psycopg2
import json
import time
import ast
import random
import hashlib
import matplotlib as mpl

schema = {
    "debate": [
        "debate_id",
        "title",
        'views'
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
        'contents_after',
        'object_id'
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

    ],
    "color": [
        'debate_id',
        'node_id',
        'user_name',
        'value'
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

    def add_view(self, debate_id):
        db = self.get_db()
        cur = db.cursor()
        cur.execute(f"""UPDATE debate  SET views = views + 1 where debate_id = (%s)""", [debate_id])
        self.conn.commit()
        cur.close()


    def get_hex_color(self, value):
        # Returns a hex color between green (0) and purple (100)
        value = max(0, min(value, 100))

        # Define color endpoints
        light_green = [0.78, 1.0, 0.796]
        light_purple = [1, 0.78, 0.968]

        # Normalize value to a range between 0 and 1
        value_norm = float(value) / 100.0

        # Interpolate between light green and light purple based on value
        color = [light_green[i] * (1 - value_norm) + light_purple[i] * value_norm for i in range(3)]

        # Return color as a hexadecimal string
        return mpl.colors.rgb2hex(color)


    def get_nodes(self, id):
        nodes = self.get_multirow_structure(id, 'node')
        new_struc = []
        for x in nodes:
            new_struc.append({
                'id': int(x['node_id']),
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


    def get_color_specific(self, debate_id, node_id):

        node_sql = f'''
                SELECT AVG(value) as average_value
                FROM color
                WHERE debate_id = (%s) and node_id = (%s);
               '''

        db = self.get_db()
        cur = db.cursor()
        cur.execute(node_sql, [debate_id, node_id])
        vals = cur.fetchall()
        self.conn.commit()
        cur.close()


        val =  self.get_hex_color(vals[0][0])
        return val
    def get_colors(self, debate_id):
        # Retrieves a list of colors for the debate.

        node_sql = f'''
                SELECT node_id, AVG(value) as average_value
                FROM color
                WHERE debate_id = (%s)
                GROUP BY node_id;
               '''

        db = self.get_db()
        cur = db.cursor()
        cur.execute(node_sql, [debate_id])
        node_rows = cur.fetchall()
        self.conn.commit()
        cur.close()
        struc = {}

        for x in node_rows:
            struc[int(x[0])] = {'hex': self.get_hex_color(x[1]), 'int':x[1]}
        print(struc)
        return struc
    def get_votes(self, debate_id):
        # Get all object votes for a debate.
        node_sql = f'''
        SELECT
          object_id,
          SUM(CASE WHEN vote = 1 THEN 1 ELSE 0 END) AS likes,
          SUM(CASE WHEN vote = -1 THEN 1 ELSE 0 END) AS dislikes,
          (SUM(CASE WHEN vote = 1 THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN vote = -1 THEN 1 ELSE 0 END), 0)) AS like_dislike_ratio
        FROM
          vote
        WHERE
            debate_id = {debate_id} and object_type = 'node'
        GROUP BY
          object_id
        '''
        edge_sql = f'''
        SELECT
          object_id,
          SUM(CASE WHEN vote = 1 THEN 1 ELSE 0 END) AS likes,
          SUM(CASE WHEN vote = -1 THEN 1 ELSE 0 END) AS dislikes,
          (SUM(CASE WHEN vote = 1 THEN 1 ELSE 0 END)::FLOAT / NULLIF(SUM(CASE WHEN vote = -1 THEN 1 ELSE 0 END), 0)) AS like_dislike_ratio
        FROM
          vote
        WHERE
            debate_id = {debate_id} and object_type = 'edge'
        GROUP BY
          object_id
        '''


        db = self.get_db()
        cur = db.cursor()
        cur.execute(node_sql)
        node_rows = cur.fetchall()
        cur.execute(edge_sql)
        edge_rows = cur.fetchall()
        self.conn.commit()
        cur.close()
        struc = {'node': {},
                 'edge': {}}

        for x in node_rows:
            struc['node'][x[0]] = {
                'likes': x[1],
                'dislikes': x[2],
                'ratio': x[3]
            }
        for x in edge_rows:
            struc['edge'][x[0]] = {
                'likes': x[1],
                'dislikes': x[2],
                'ratio': x[3]
            }
        print(struc)
        return struc

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
                           FROM debate
                           order by views desc""")


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


    def get_user_vote(self, debate_id,  user_id):
        # Return a JSON of objects the user has voted on
        sql_node = f'''
        select object_id, vote, user_name from vote
        where user_name = '{user_id}' and debate_id = {debate_id} and object_type = 'node'
        
        '''
        sql_edge = f'''
        select object_id, vote, user_name from vote
        where user_name = '{user_id}' and debate_id = {debate_id} and object_type = 'edge' '''

        db = self.get_db()
        cur = db.cursor()
        cur.execute(sql_node)
        node_rows = cur.fetchall()
        cur.execute(sql_edge)
        edge_rows = cur.fetchall()
        self.conn.commit()
        cur.close()
        obj = {'nodes': {},
        'edges': {}}
        for x in node_rows:
            obj['nodes'][x[0]] = x[1]
        for x in edge_rows:
            obj['edges'][x[0]] = x[1]


        return obj

    def update_node(self, debate_id, node_id, update, user_id, original):
        sql = '''
               update node 
               set contents = (%s)
               where debate_id = (%s) and node_id = (%s);
            
               
               '''

        db = self.get_db()
        cur = db.cursor()
        cur.execute(sql, ( update, debate_id, node_id))


        self.conn.commit()
        cur.close()
        self.add_multirow_structure('edit', [
            {
                'debate_id': debate_id,
                'edit_id': random.randint(0, 2147483647),
                'user_id': user_id,
                'timestamp': str(datetime.datetime.now()),
                'object_type': 'node',
                'contents_before': original,
                'contents_after': update,
                'object_id': node_id


            }

        ])


    def update_color_vote(self, debate_id, node_id, vote, user_id):
        # Update the database with the votes of the user
        assert vote > -1 and vote < 101
        sql = '''
        INSERT INTO color (debate_id, node_id, user_name, value, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (debate_id, node_id, user_name)
        DO UPDATE SET
          value = EXCLUDED.value,
          timestamp = EXCLUDED.timestamp
        '''

        db = self.get_db()
        cur = db.cursor()
        cur.execute(sql, (debate_id, node_id, user_id, vote, str(datetime.datetime.now())))
        self.conn.commit()
        cur.close()


    def update_vote(self, debate_id, object_type, object_id, vote, user_id):
        # Update the database with the votes of the user
        sql = '''
        INSERT INTO vote (debate_id, object_type, object_id, user_name, timestamp, vote)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (debate_id, object_type, object_id, user_name)
        DO UPDATE SET
          vote = EXCLUDED.vote,
          timestamp = EXCLUDED.timestamp;
        '''

        db = self.get_db()
        cur = db.cursor()
        cur.execute(sql, (debate_id, object_type, object_id, user_id, str(datetime.datetime.now()), vote))
        self.conn.commit()
        cur.close()

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