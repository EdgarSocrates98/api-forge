import subprocess
from neo4j import GraphDatabase


def boot():
    return subprocess.run(['ls'])
