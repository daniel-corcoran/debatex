import psycopg2
import json
import time
import ast
import random

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
    "user": [
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




    def get_nodes(self, id):
        return None

    def get_edges(self, id):
        return None

    def get_votes(self, id):
        return None

    def add_debate(self, struc):
        ...


    def get_debate_list(self):
        ...
        return [
            {
                'debate_id': 1,
                'title': "Should Abortion Be Legal?"
            }
        ]

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