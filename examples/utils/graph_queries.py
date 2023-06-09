from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

graph = Graph()
graph_db_uri = 'ws://127.0.0.1:8182/gremlin'

      
g = graph.traversal().withRemote(DriverRemoteConnection(graph_db_uri,'g'))
count=g.V().count().next()
print("vertex count: ",count)

count=g.E().count().next()
print("edge count: ",count)