'''
__author__ = "Samuel Carlisle"
__copyright__ = "Copyright 2012"
__credits__ = ["Samuel Carlisle, Martin Clarke, Alan Ross, Elizabeth Richardson"]
__license__ = "GPL Affero"
__version__ = "3"
__maintainer__ = "Samuel Carlisle"
__email__ = "samuelcarlisle@gmail.com"
__status__ = "Development"
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

whatissukey is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

whatissukey is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero Public License
along with whatissukey.  If not, see <http://www.gnu.org/licenses/>.
'''
import humanio
import my_humanio_auth

def main():
    app = humanio.App(my_humanio_auth.developer_id,
                      my_humanio_auth.secret_key,
                      public=False)
    print "Connecting to the 1984 darknet listening posts...viva la resistance!"
    app.create_task(description="What is Sukey.io?",
                    humans_per_item=-1, #humans_per_item - How many people you are requesting. Specify -1 for unlimited number
                    thumbnail="http://sukey.io/images/info.gif",
                    human_can_do_multiple=True,
                    #auto_repeat=None,
                    #camera=True, #you need a camera for this activity! Disable for testing
                    on_connect_fn=on_connect,
                    on_submit_fn=on_submit)
    print "System online, tl;dr; only an excuse for teh real n00bs..."
    app.start_loop()

def on_connect(session, task, item):
    """This is called when the human clicks on our task in his client app."""

    print "Human connected, explaing what sukey.io is..."
    session.add_image("http://sukey.org/images/app/loadsukey.gif", decorated=False)
    session.add_text("Sukey.io helps you have fun during the protests and, on the way, keep each other safe, mobile and informed.")
    session.add_text("This leaves no trace, the micro-app list is temporary and set by Sukey servers.")
    session.add_text("No installation or removal is required and they can be used immediately.")
    session.add_text("Micro-apps are frequently updated and change based on your location, keep checking Sukey.io during the protest to see what's new.")
    session.add_submit_button("Done")

def on_submit(session, task, form_data):
    """This is called when the human clicks the "Done" button we created
    in the connect callback."""

    print "Human has read the page, dismissing..."
    print "Standing-by waiting for moar humans..."
    session.dismiss(approve=True)

if __name__ == "__main__":
    main()
