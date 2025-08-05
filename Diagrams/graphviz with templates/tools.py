from graphviz import Digraph

class Method:
    def __init__(self, name, parent_class):
        self.name = name
        self.parent = parent_class
        self.port = f"{self.parent._next_port()}"
        self.parent._add_method(self)

    def connect(self, target_method, label=""):
        self.parent.graph._add_edge(
            f"{self.parent.id}:{self.port}",
            f"{target_method.parent.id}:{target_method.port}",
            label
        )

class Class:
    def __init__(self, name, graph, id=None):
        self.name = name
        self.id = id or name.replace(" ", "_")
        self.graph = graph
        self.methods = []
        self._port_count = 1
        graph._add_class(self)

    def _add_method(self, method_obj):
        self.methods.append(method_obj)

    def _next_port(self):
        port = f"m{self._port_count}"
        self._port_count += 1
        return port

    def to(self, other_class, label=""):
        self.graph._add_edge(self.id, other_class.id, label)

class User:
    def __init__(self, label, graph, id=None):
        self.name = label
        self.id = id or label.replace(" ", "_")
        self.graph = graph
        graph._add_user(self)

    def connect(self, target_method, label=""):
        self.graph._add_edge(
            self.id,
            f"{target_method.parent.id}:{target_method.port}",
            label
        )

class Graph:
    def __init__(self, name="ClassDiagram", direction="LR", output_format="pdf"):
        self.name = name
        self.graph = Digraph(name=name, format=output_format)
        self.graph.attr(rankdir=direction, fontname="Consolas")
        self.graph.attr("node", shape="plaintext", fontname="Consolas")
        self.classes = {}
        self.users = {}

    def _add_class(self, class_obj):
        self.classes[class_obj.id] = class_obj

    def _add_user(self, user_obj):
        self.users[user_obj.id] = user_obj
        self.graph.node(user_obj.id, label=f"👤 User", shape="plaintext")

    def _add_edge(self, from_id, to_id, label=""):
        self.graph.edge(from_id, to_id, label=label)

    def render(self, filename="diagram", view=True):
        for class_obj in self.classes.values():
            self._render_class(class_obj)
        self.graph.render(filename, view=view)

    def _render_class(self, cls):
        rows = "".join(
            f'<TR><TD PORT="{method.port}">{method.name}</TD></TR>'
            for method in cls.methods
        )
        label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD BGCOLOR="lightblue"><B>{cls.name}</B></TD></TR>
            {rows}
        </TABLE>>'''
        self.graph.node(cls.id, label=label)
