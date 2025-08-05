from graphviz import Digraph

dot = Digraph(comment='Class Instantiation Flow')

dot.node('U', 'User Code')
dot.node('C', 'MyClass')
dot.node('I', 'MyClass Instance')

dot.edge('U', 'C', label='calls constructor')
dot.edge('C', 'I', label='creates')

dot.render('flowchart', format='svg', view=True)