Was playing blackjack at a resort casino and decided that I wanted to get good. So, I've been working on this project.

At first this was a blackjack game engine I made from scratch in python, playable in the console. The rules of the blackjack table are adjustable, and all the different aspects of the game, the card system, player systems, etc. are all coded from scratch using only some basic python libraries and numpy (blackjack.py, cards.py).

In addition to the game engine I also decided to see if I could, from scratch, calculate those optimal basic strategy tables (like this one https://m.media-amazon.com/images/I/816DFf5i0EL._AC_UF1000,1000_QL80_.jpg) based on the adjusted rules and (optionally) the amount of each different card left in the deck (bjodds.py).

After that's done the final part of this project is going to be making a DL model that learns to play blackjack perfectly using my engine, so we'll see how that goes. (this is what I'm currently working on, blackjackbot.py)
