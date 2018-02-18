
# I could make five main tasks, one per priority, with everything being a subtask?

import json
from bs4 import BeautifulSoup

# pip install BeautifulSoup4

with open(r'C:\Users\Dag.Calafell\Documents\GitHub\Toodledo-To-Nozbe\toodledo.xml', 'r') as myfile:
    data = myfile.read().replace('\n', '')

soup = BeautifulSoup(data, 'html.parser')

data = {}
data['data'] = {'lists': [], 'tasks': [], 'subtasks': [], 'notes': [], 'task_positions': [], 'subtask_positions': []}

# Build list of Toodledo: Folders which will become Wunderlist "lists"
# this first loop is to remove duplicates
x = []
for item in soup.findAll('folder'):
    if item.text not in x:
        x.append(item.text)

## Now add them as lists to the json output data
i = 0
listIds = {}
for folder_name in x:
    i = i + 1
    data['data']['lists'].append({"id": i, "title": folder_name, "list_type": "list"})
    listIds[folder_name] = i

dictUnsupportedFields = {}
dictUnsupportedFields['repeating tasks'] = 0
dictUnsupportedFields['timer values'] = 0
dictUnsupportedFields['complex due dates'] = 0
dictUnsupportedFields['due times'] = 0
dictUnsupportedFields['lengths'] = 0
dictUnsupportedFields['locations'] = 0
dictUnsupportedFields['goals'] = 0
dictUnsupportedFields['statuses'] = 0
dictUnsupportedFields['start dates and times'] = 0

dictNotes = {}

i = 0
for item in soup.findAll('item'):
    i = i + 1
    #if i == 16: break ################################# Testing

    t_id = item.id.text
    t_title = item.title.text
    t_folder = item.folder.text
    t_duedate = item.duedate.text
    t_completed = item.completed.text
    t_star = item.star.text
    t_note = item.note.text

    # I need these, for now I've put them in the title
    t_order = item.order.text
    t_parent = item.parent.text
    t_priority = item.priority.text
    t_context = item.context.text
    t_tag = item.tag.text

    # not converted into target file
    t_duedatemodifier = item.duedatemodifier.text
    t_duetime = item.duetime.text
    t_goal = item.goal.text
    t_length = item.length.text
    t_location = item.location.text
    t_repeat = item.repeat.text
    t_repeatfrom = item.repeatfrom.text
    t_startdate = item.startdate.text
    t_starttime = item.starttime.text
    t_status = item.status.text
    t_timer = item.timer.text

    if t_repeat != 'None':
        dictUnsupportedFields['repeating tasks'] = dictUnsupportedFields['repeating tasks'] + 1
    if t_timer != '0':
        dictUnsupportedFields['timer values'] = dictUnsupportedFields['timer values'] + 1
    if t_duedatemodifier != '0':
        dictUnsupportedFields['complex due dates'] = dictUnsupportedFields['complex due dates'] + 1
    if t_duetime != '':
        dictUnsupportedFields['due times'] = dictUnsupportedFields['due times'] + 1
    if t_length != '':
        dictUnsupportedFields['lengths'] = dictUnsupportedFields['lengths'] + 1
    if t_location != '':
        dictUnsupportedFields['locations'] = dictUnsupportedFields['locations'] + 1
    if t_goal != '':
        dictUnsupportedFields['goals'] = dictUnsupportedFields['goals'] + 1
    if t_status != 'None':
        dictUnsupportedFields['statuses'] = dictUnsupportedFields['statuses'] + 1
    if t_startdate != "0000-00-00" or t_starttime != '':
        dictUnsupportedFields['start dates and times'] = dictUnsupportedFields['start dates and times'] + 1

    val_starred = False
    if t_star == "1":
        val_starred = True

    val_complete = False
    val_completedAt = ''
    if t_completed != "0000-00-00":
        val_complete = True
        val_completedAt = t_completed + 'T08:00:00.000Z'

    if t_note != '':
        dictNotes[t_id] = t_note

    # Build a composite title
    v_title = t_title
    if t_context != '':
        v_title = "%s %s" % (v_title, t_context)
    if t_priority != '':
        v_title = "-%s %s" % (t_priority, v_title)
    if t_status != 'None':
        v_title = "-%s %s" % (t_status, v_title)
    if t_tag != '':
        v_title = "%s %s" % (v_title, t_tag)

    data['data']['tasks'].append({"id": t_id, "completed": val_complete, "completed_at": val_completedAt, "starred": val_starred, "title": v_title, "list_id": listIds[t_folder]})

# Add notes to the json data
for taskID in dictNotes.keys():
    data['data']['notes'].append({"task_id": taskID, "content": dictNotes[taskID]})

# Warn the user of unsupported fields
for unsupported_field in dictUnsupportedFields.keys():
    i = dictUnsupportedFields[unsupported_field]
    if i > 0:
        print('WARNING: %s are not supported (%d occurences).' % (unsupported_field, i))

# Dump the file
with open('Import-into-Nozbe.json', 'w') as outfile:
    json.dump(data, outfile)

print('Done.')
