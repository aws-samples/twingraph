######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################


from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
import json
import ast

from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import Cardinality
from gremlin_python import statics
from gremlin_python.process.traversal import Column

statics.load_statics(globals())


def to_string(obj):
    return json.dumps(obj)


def init_reset_graph(gremlin_IP):
    connection = DriverRemoteConnection(gremlin_IP, 'g')

    graph = Graph()
    g = graph.traversal().withRemote(connection)
    g.V().drop().iterate()

    connection.close()

    pass


def add_vertex_connection(gremlin_IP, attributes):
    connection = DriverRemoteConnection(gremlin_IP, 'g')

    graph = Graph()
    g = graph.traversal().withRemote(connection)

    # prepare the add vertex sub traversal
    add_vertex_traversal = __.addV(attributes["Name"])
    for k, v in attributes.items():
        add_vertex_traversal = add_vertex_traversal.property(k, v)

    g.V().has("origin_node", 'origin_val').fold().coalesce(
        __.unfold(), add_vertex_traversal).next()

    # print('Added Vertex',g.V().has('Hash', attributes['Hash']))
    if attributes['Parent Hash'] != '':
        for hash in ast.literal_eval(attributes['Parent Hash']):
            g.V().has('Hash', hash).as_("a").V().has('Hash', attributes['Hash']).as_("b").addE(
                g.V().has('Hash', hash).values('Output').next()).from_("a").to("b").iterate()
            # print('& Connections to', g.V().has('Hash', hash))

    # print('Properties:\n')

    # for p in g.V().has('Hash', attributes['Hash']).properties():
    #    print("key:",p.label, "| value: " ,p.value)

    connection.close()
    pass
