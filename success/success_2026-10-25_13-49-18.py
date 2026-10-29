import json

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, title, priority):
        if priority not in ['low', 'medium', 'high']:
            raise ValueError("Priority must be 'low', 'medium', or 'high'."[8D[K
'high'.")
        self.tasks.append({'title': title, 'priority': priority})

    def get_tasks_by_priority(self, priority):
        return [task for task in self.tasks if task['priority'] == priority[8D[K
priority]

    def save_to_json(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.tasks, file)

    def load_from_json(self, filename):
        try:
            with open(filename, 'r') as file:
                self.tasks = json.load(file)
        except FileNotFoundError:
            print("File not found. Creating a new list of tasks.")
            self.tasks = []

# Example usage
task_manager = TaskManager()
task_manager.add_task("Task 1", "high")
task_manager.add_task("Task 2", "medium")
task_manager.add_task("Task 3", "low")
task_manager.save_to_json("tasks.json")

task_manager.load_from_json("tasks.json")
high_priority_tasks = task_manager.get_tasks_by_priority("high")
for task in high_priority_tasks:
    print(f"Title: {task['title']}, Priority: {task['priority']}")