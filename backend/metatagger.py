'''
__author__ = "Samuel Carlisle"
__copyright__ = "Copyright 2012"
__credits__ = ["Samuel Carlisle, Martin Clarke, Alan Ross"]
__license__ = "GPL Affero"
__version__ = "3"
__maintainer__ = "Samuel Carlisle"
__email__ = "samuelcarlisle@gmail.com"
__status__ = "Prototype"
enumerate(__status__):"Prototype", "Development", or "Production". 
                                                       ____
           ___                                      .-~. /_"-._        ________________________________
          `-._~-.                                  / /_ "~o\  :Y      /We made Sukey.io so that people \
              \  \                                / : \~x.  ` ')      |can have fun during the protests|
               ]  Y                              /  |  Y< ~-.__j      |and, on the way, keep each other|
              /   !                        _.--~T : l  l<  /.-~      < safe, mobile and informed (;..;)|
             /   /                 ____.--~ .   ` l /~\ \<|Y          \________________________________/
            /   /             .-~~"        /| .    ',-~\ \L|
           /   /             /     .^   \ Y~Y \.^>/l_   "--'
          /   Y           .-"(  .  l__  j_j l_/ /~_.-~    .
         Y    l          /    \  )    ~~~." / `/"~ / \.__/l_
         |     \     _.-"      ~-{__     l  :  l._Z~-.___.--~
         |      ~---~           /   ~~"---\_  ' __[>
         l  .                _.^   ___     _>-y~
          \  \     .      .-~   .-~   ~>--"  /
           \  ~---"            /     ./  _.-'
            "-.,_____.,_  _.--~\     _.-~
                        ~~     (   _}  
                                `. ~(
                                  )  \
                                 /,`--'~\--'
This file is part of Sukey.io.

tagger is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

tagger is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero Public License
along with tagger.  If not, see <http://www.gnu.org/licenses/>.
'''
"""
A simple task which requests people to photgraph banners and placards and rate those of others.
"""

import humanio
import random
import my_humanio_auth
thanks_array = ["You rock!","Thanks!", "Great Stuff!", "Merci beaucoup!", "Got it!", "Danke schon!", "Nice photo!", "Omnomnom... Photo!", "Yay!"]
#welcome_array = ["Hi!", "Hello!", "Ola!", "Bonjour", "Heya!"]
def main():
    app = humanio.App(my_humanio_auth.developer_id,
                      my_humanio_auth.secret_key,
                      public=False)
    print "Connecting to the 1984 darknet listening posts...viva la resistance!"
    app.create_task(description="Photo Tagger", #rename to epic signage?
                    humans_per_item=-1, #humans_per_item - How many people you are requesting. Specify -1 for unlimited number
                    thumbnail="http://sukey.io/images/photo.gif",
                    human_can_do_multiple=True,
                    #auto_repeat=None,
                    #camera=True, #you need a camera for this activity! Disable for testing
                    on_connect_fn=on_connect,
                    on_submit_fn=on_submit,
                    latitude=51.524579, longitude=-0.082312, #currently centered on London Hackspace
                    radius_miles=10)
    print "System online, standing by for field reports..."
    app.start_loop()

def on_connect(session, task, item):
    session.add_text("Please Tag all the things that come to mind with.")
    session.add_text("")
    session.add_rating_selector("my_rating_selector", number_of_stars=10)
    session.add_text("")
    session.add_submit_button("Done")

def on_submit(session, task, form_data):
    """This is called when the human clicks the "Done" button we created
    in the connect callback."""

    print "Human has finished rating shit and wants another biscuit..."
    print "Standing-by waiting for moar humans..."
    session.dismiss(approve=True)

if __name__ == "__main__":
    main()
