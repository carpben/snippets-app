import argparse
import sys
import logging
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect("dbname='snippets'")
logging.debug("Database connection established.")

def put(name, snippet):
    """
    Store a snippet with an associated name. Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        try: 
            command = "insert into snippets values (%s, %s)"
            cursor.execute(command, (name, snippet))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = "update snippets set message=%s where keyword=%s"
            cursor.execute(command, (snippet, name))
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
def get(name):
    """
    Retrieve the snippet with a given name.

    Returns the snippet.
    """
    logging.info("Retriving snippet {!r}.".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        snippet = cursor.fetchone()
    logging.debug("Snippet Retrieved successfully. Snippet Value: {}".format(snippet))
    if snippet == None:
        # No snippet was found with that name.
        return snippet
    return snippet[0]

def catalog():
    """
    Presents a Catalog of Snippets names. 
    """
    logging.info("About to present catalog of names.")
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets")
        catalog = cursor.fetchall()
    return catalog

def search(string): 
    """
    Searches for snippets with the string
    """
    logging.info("About to search for snippets with the the string:'{}'".format(string))
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets where message like '%{}%'".format(string))
        results = cursor.fetchall()
        return results
    
def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="The name of the snippet")
    put_parser.add_argument("snippet", help="The snippet text")

    # Subparser for the get command
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="The name of the snippet")
    
    catalog_parser=subparsers.add_parser("catalog", help="Presents a catalog of snippets names")
    
    search_parser=subparsers.add_parser("search", help="User provides a string. Prgram Searches for snippets with the string andprints results to screen.")
    search_parser.add_argument("string", help="String to search for")
    
    logging.debug('{}\nparser.parse_args():\n{}'.format('-'*20, parser.parse_args()))
    
    arguments = parser.parse_args()
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    
    command = arguments.pop("command")
    logging.debug('{}\narguments:{}'.format('-'*20, arguments))
    
    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        if snippet==None: 
            print("No snippet stored for name: '{}'".format(arguments['name']))
        else: 
            print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
        cata=catalog()
        print (cata)
    elif command == "search": 
        results = search(**arguments)
        print results
    else: 
        "Command not recognized." 
    
if __name__ == "__main__":
    main()