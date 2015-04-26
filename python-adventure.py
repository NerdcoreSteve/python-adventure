player_name = ''

player_name = raw_input("What's your name? ")

game_data = {"one-room house" : {"description" : "You're name is " + player_name + ". You're darkly lit one-room house. Its raining outside. You can hear the drops hit the ceiling and can see rain hit the window when lightning strikes in the distance, which it often does. The window is above a sink which is full of dirty dishes. On the oven beside the sink there is a pot full of boiling water. To your left there is a couch facing a television. The power's out so it's not on. Amazingly there's a penguin sitting on the couch, but they've turned to face you. Behind you is a pile of smelly blankets and an old set of golf clubs.",
                                  "choices" : [{"input" : "t",
                                               "description" : "talk to the penguin"}]},
"penguin conversation" : {"description" : "You say, \"Hello penguin.\"\n\n\"Hello " + player_name + ",\" replies the penguin."}}

print ""

current_room = game_data['one-room house']
choices = current_room['choices']

print current_room['description']

player_input = ''
while player_input != 'q':
    print ""

    choice = choices[0]['input']
    description = choices[0]['description']

    print choice + ") " + description
    print "q) quit game"

    print ""

    player_input = raw_input("What will you do? ")

    print ""

    if player_input == 't':
        print game_data['penguin conversation']['description']
    elif player_input == 'q':
        print "Hope you had fun!"
    else:
        print "I have no idea what you're talking about."
