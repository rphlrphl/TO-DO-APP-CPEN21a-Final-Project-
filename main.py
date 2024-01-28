# main.py
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from database import Database
import platform
from plyer import notification
import time
import threading
from kivy.core.audio import SoundLoader



if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


db = Database()



class MainApp(MDApp):
    task_list_dialog = None # Here
    def build(self):
        # Setting theme to my favorite theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.2


    def switch_theme_style(self):
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )

    # Add the below functions
    def show_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="[color=FFA500]Create Task[/color]",
                type="custom",
                content_cls=DialogContent(),

            )

        self.task_list_dialog.open()



    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    def add_task(self, task, task_date):
        '''Add task to the list of tasks'''

        # Add task to the db
        created_task = db.create_task(task.text, task_date)  # Here

        # return the created task details and create a list item
        self.root.ids['container'].add_widget(
            ListItemWithCheckbox(pk=created_task[0], text= created_task[1],
                                 secondary_text=created_task[2]))  # Here
        task.text = ''





    def on_start(self):
        """Load the saved tasks and add them to the MDList widget when the application starts"""
        try:
            completed_tasks, uncomplete_tasks = db.get_tasks()

            if uncomplete_tasks != []:
                for task in uncomplete_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0], text=task[1], secondary_text=task[2])
                    self.root.ids.container.add_widget(add_task)

            if completed_tasks != []:
                for task in completed_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0], text='[s]' + task[1] + '[/s]', secondary_text=task[2])
                    add_task.ids.check.active = True
                    self.root.ids.container.add_widget(add_task)
        except Exception as e:
            print(e)
            pass



class DialogContent(MDBoxLayout): # This gets the tasks from the user
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # set the date_text label to today's date when useer first opens dialog box
        self.ids.date_text.text = str(datetime.now().strftime('[color=FFA500]%A %d %B %Y[/color]'))
        self.ids.date_text.markup = True

    def show_date_picker(self): # Shows the date picker
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range): # Gets the date picker
        date = value.strftime('[color=FFA500]%A %d %B %Y[/color]')
        self.ids.date_text.text = str(date)
        self.ids.date_text.markup = True

class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    '''Custom list item'''

    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def mark(self, check, the_list_item):
        '''mark the task as complete or incomplete'''
        if check.active == True:
            the_list_item.text = '[s]' + the_list_item.text + '[/s]'
            db.mark_task_as_complete(the_list_item.pk)  # here
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk))  # Here

    def delete_item(self, the_list_item):
        '''Delete the task'''
        self.parent.remove_widget(the_list_item)
        db.delete_task(the_list_item.pk)# Here


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    '''Custom left container'''

class NotificationThread(threading.Thread):
    def run(self):
        while True:
            time.sleep(60)
            notification.notify(
                title="You still have things to do!",
                message="Get up and do your things!",
                app_name='do!',
                app_icon='icon.ico',
                timeout=20
            )
            sound = SoundLoader.load('notification.mp3')
            sound.play()


# Start the notification thread
notification_thread = NotificationThread()
notification_thread.start()



app = MainApp()
app.run()
