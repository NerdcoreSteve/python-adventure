import re

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

#TODO should grab this from a .game file
game_data = \
    {
        "one-room house":
            {
                "description": "Your name is {{player name}}. You're in a darkly lit one-room house. Its raining outside. You can hear the drops hit the ceiling and can see rain hit the window when lightning strikes in the distance, which it often does. The window is above a sink full of dirty dishes. On the oven beside the sink there is a pot full of boiling water. To your left there is a couch facing a television. It's turned to a channel that only gets static. Amazingly there's a penguin sitting on the couch. The penguin turns to face you when you look at it. Behind you is a pile of smelly blankets and an old set of golf clubs.",
                "choices":
                    [
                        {
                            "input": "t",
                            "description": "Talk to the penguin",
                            "destination": "penguin conversation"
                        },
                        {
                            "input": "l",
                            "description": "Look around the room again",
                            "destination": "one-room house"
                        }
                    ]
            },
        "penguin conversation":
            {
                "description":
                    "You say, \"Hello penguin.\"\n\n\"Hello {{player name}},\" replies the penguin.",
                "choices":
                    [
                        {
                            "input": "l",
                            "description": "look around the room again",
                            "destination": "one-room house"
                        },
                        {
                            "input": "a",
                            "description": "Ask the penguin what's going on.",
                            "destination": "penguin says what's up"
                        },
                        {
                            "input": "n",
                            "description": "Ask the penguin their name.",
                            "destination": "name the penguin"
                        }
                    ]
            },
        "penguin says what's up":
            {
                "description":
                    "You say, \"What's going on?\"\n\n\"I heard a loud bang outside. I think someone's out there.\" replies the penguin.\n\nJust then, you hear a loud noise. Some thing or some one just hit the wall with a loud thud.",
                "choices":
                    [
                        {
                            "input": "l",
                            "description": "look around the room again",
                            "destination": "one-room house"
                        },
                        {
                            "input": "n",
                            "description": "Ask the penguin their name.",
                            "destination": "name the penguin"
                        }
                    ]
            },
        "name the penguin":
            {
                "description":
                    "You say, \"What's your name?\"\n\nThe penguin says, \"You remember it's...\"",
                "choices":
                    [
                        {
                            "input" : "l",
                            "description" : "look around the room again",
                            "destination" : "one-room house"
                        }
                    ]
            }
    }

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
                current_room = game_data[choice["destination"]]
                valid_choice = True

        if not valid_choice:
            print "I have no idea what you're talking about."
