import threading
import time

# Create an event to signal when one of the tasks has completed
task_completed = threading.Event()

# Define your two tasks as functions
def task1():
    print("Task 1 started")
    time.sleep(2)
    print("Task 1 finished")
    task_completed.set()  # Signal that Task 1 is completed

def task2():
    print("Task 2 started")
    time.sleep(1)
    print("Task 2 finished")
    task_completed.set()  # Signal that Task 2 is completed

if __name__ == "__main__":
    # Create two threads for the tasks
    thread1 = threading.Thread(target=task1)
    thread2 = threading.Thread(target=task2)

    # Start both threads
    thread1.start()
    thread2.start()

    # Wait for either task to complete
    task_completed.wait()

    print("One of the tasks has completed")