import os
import json
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

TASKS_FILE = os.path.expanduser('~/.config/ulauncher-todo-tasks.json')

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

class TodoExtension(Extension):
    def __init__(self):
        super(TodoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        items = []
        tasks = load_tasks()
        
        if query.strip():
            # Show option to add new task
            items.append(
                ExtensionResultItem(
                    icon='images/icon.png',  
                    name=f"Add task: {query.strip()}",
                    description="Press Enter to save this task",
                    on_enter=ExtensionCustomAction({"action": "add_task", "task": query.strip()})
                )
            )
        
        # Show all tasks
        if not tasks:
            items.append(
                ExtensionResultItem(
                    icon='images/icon.png', 
                    name="No tasks found." if not query.strip() else "No existing tasks.",
                    description="",
                    on_enter=DoNothingAction()
                )
            )
        else:
            for i, task in enumerate(tasks):
                items.append(
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name=task,
                        description="Press Enter to remove this task",
                        on_enter=ExtensionCustomAction({"action": "remove_task", "index": i})
                    )
                )
                
        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        tasks = load_tasks()
        
        if data["action"] == "add_task":
            tasks.append(data["task"])
            save_tasks(tasks)
        elif data["action"] == "remove_task":
            if 0 <= data["index"] < len(tasks):
                del tasks[data["index"]]
                save_tasks(tasks)
                
        return RenderResultListAction([
            ExtensionResultItem(
                icon='images/icon.png',  
                name="Task updated successfully!",
                description="",
                on_enter=DoNothingAction()
            )
        ])

if __name__ == '__main__':
    TodoExtension().run()
