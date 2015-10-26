import re
import json

#TODO should grab this from a .save file
saved_data = {}

def name_entity(saved_data, options):
    saved_data[options['label']] = raw_input(options['prompt'] + " ")

# TODO maybe this should say something like {{player name}} got a {{item}}! or got another {{item}}!
# TODO I'll need a way for the environment to keep track of how many items there are
#      this function will probably have to account for that.
def add_to_inventory(saved_data, options):
    if options['item'] in saved_data['inventory']:
        saved_data['inventory'][options['item']] += 1
    else:
        saved_data['inventory'][options['item']] = 1

actions = {'name_entity' : name_entity, 'add_to_inventory' : add_to_inventory}

actions['name_entity'](saved_data, {"prompt" : "What's your name?", "label" : "player name"})

#TODO make choice have an optional action, if there is an action, call one of the actions functions.
#     Then you won't need this call to name_entity up here, you start with a 'room' that introduces
#     the game and then goes to the one-room-house

with open('python-adventure.game') as game_file:    
    game_data = json.load(game_file)

def add_saved_data(string):
    matches = re.search("\{\{(.*?)\}\}", string)
    if(matches):
        default = matches.group(1)
        return add_saved_data(
                re.sub(
                    matches.group(0),
                    saved_data[default] if default in saved_data else default,
                    string))
    else:
        return string

#TODO .game file should tell us this
current_room = game_data["one-room house"]

player_input = ""
while player_input != "q":
    print "\n" + add_saved_data(current_room["description"]) + "\n"

    #TODO game data should be able to specify a set of default choices you usually always have.
    for choice in current_room["choices"]:
        print choice["input"] + ") " + add_saved_data(choice["description"])
    print "q) quit game\n"

    player_input = raw_input("What will you do? ")

    if player_input == "q":
        print "Hope you had fun!"
    else:
        valid_choice = False

        for choice in current_room["choices"]:
            if player_input == choice["input"]:
                if "action" in choice and choice["action"]["name"] in actions:
                    actions[choice["action"]["name"]](saved_data, choice["action"]["options"])
                current_room = game_data[choice["destination"]]
                valid_choice = True

        if not valid_choice:
            print "I have no idea what you're talking about."
