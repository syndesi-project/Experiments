from tools import Graph, Class, Method, User

graph = Graph()

# Classes and methods
graph.my_class = Class("Backend", graph)
graph.my_class.method1 = Method("connect()", graph.my_class)

graph.my_class2 = Class("Worker", graph)
graph.my_class2.method2 = Method("run()", graph.my_class2)

# User
graph.user = User("Client App", graph)

# Arrows
graph.user.connect(graph.my_class.method1, "calls")
graph.my_class.method1.connect(graph.my_class2.method2, "spawns")

graph.render("user_flow_diagram")
