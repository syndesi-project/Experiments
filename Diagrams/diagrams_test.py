from diagrams import Diagram
from diagrams.custom import Custom

with Diagram("Class Flow", direction="LR", filename='class_flow', ):
    user = Custom("User", "./user_icon.png")
    class_ = Custom("MyClass", "./class_icon.png")
    instance = Custom("Instance", "./object_icon.png")

    user >> class_ >> instance