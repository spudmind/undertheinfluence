import types


def get_identity(vertex):
    identifiers = ['name', 'term', 'title', 'node_name']
    properties = vertex.data()
    for identity in identifiers:
        if identity in properties:
            return properties[identity], identity


def get_vertex_properties(vertex):
    properties = vertex.data()
    for k, v in properties.iteritems():
        print k, ':', v


def get_edges(vertex):
    edges = []
    out_vertices = vertex.outE()
    if out_vertices:
        for e in out_vertices:
            edges.append(
                (e.eid,
                 get_identity(e.outV()),
                 e.label(),
                 get_identity(e.inV()))
            )
    in_vertices = vertex.inE()
    if in_vertices:
        for e in in_vertices:
            edges.append(
                (e.eid,
                 get_identity(e.outV()),
                 e.label(),
                 get_identity(e.inV()))
            )
    return edges


def get_articles(vertex):
    articles = []
    in_vertices = vertex.inE()
    if in_vertices:
        for e in in_vertices:
            if e.label() == 'mentions':
                vertex_in = e.outV()
                properties = vertex_in.data()
                articles.append(
                    (
                        (properties['title'], properties['content']),
                        e.label(),
                        get_identity(e.inV())
                    )
                )
    else:
        out_vertices = vertex.outE()
        for e in out_vertices:
            if e.label() == 'mentions':
                vertex_out = e.inV()
                properties = vertex_out.data()
                articles.append(
                    (
                        get_identity(e.outV()),
                        e.label(),
                        (properties['title'], properties['content'])
                    )
                )

    return articles


def get_node(graph, search, node_type):
    if node_type == 'NamedEntity':
        vertices = graph.vertices.index.lookup(name=search)
    elif node_type == 'UniqueTerm':
        vertices = graph.vertices.index.lookup(term=search)
    elif node_type == 'Article':
        vertices = graph.vertices.index.lookup(title=search)
    elif node_type == 'PolicyAgenda':
        vertices = graph.vertices.index.lookup(node_name=search)
    elif node_type == 'PolicyCategory':
        vertices = graph.vertices.index.lookup(node_name=search)
    else:
        vertices = False
    if isinstance(vertices, types.GeneratorType):
        vertex = vertices.next()
        return vertex
    else:
        return False


def get_term(graph, term):
    # vertices = graph.vertices.index.lookup(term=term)
    vertices = get_node(graph, term, 'term')
    get_edges(vertices)


def get_name(graph, name):
    vertices = get_node(graph, name, 'name')
    get_edges(vertices)