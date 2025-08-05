from graphviz import Digraph

# --- Settings ---
OUTPUT_FILE = "class_diagram"
OUTPUT_FORMAT = "pdf"  # or "svg", "png"

# --- Class Metadata (define here!) ---
classes = {
    "UserCode": {
        "methods": ["main()", "connect()"]
    },
    "ConnectionManager": {
        "methods": ["__init__()", "start_thread()", "stop()"]
    },
    "WorkerThread": {
        "methods": ["run()", "join()", "terminate()"]
    },
}

# --- Relationships (from → to, with label) ---
links = [
    ("UserCode", "ConnectionManager", "creates"),
    ("ConnectionManager", "WorkerThread", "spawns"),
]

# --- Graph Construction ---
dot = Digraph(comment="Class Diagram", format=OUTPUT_FORMAT)
dot.attr(rankdir="LR", fontsize="12", fontname="Consolas")
dot.attr("node", shape="plaintext", fontname="Consolas")

# Function to create a "class-like" table node
def class_node(name, methods):
    label = f"""<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
    <TR><TD BGCOLOR="lightblue"><B>{name}</B></TD></TR>
    {''.join(f'<TR><TD>{m}</TD></TR>' for m in methods)}
    </TABLE>>"""
    dot.node(name, label=label)

# Add all class nodes
for cls_name, data in classes.items():
    class_node(cls_name, data["methods"])

# Add edges
for src, dst, label in links:
    dot.edge(src, dst, label=label)

# Render
dot.render(OUTPUT_FILE, view=True)
