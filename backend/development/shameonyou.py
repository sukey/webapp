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

shameonyou is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

shameonyou is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero Public License
along with shameonyou.  If not, see <http://www.gnu.org/licenses/>.
'''

import humanio
import random
import my_humanio_auth
thanks_array = ["You rock!","Thanks!", "Great Stuff!", "Merci beaucoup!", "Got it!", "Danke schon!", "Nice photo", "Omnomnom... Photo", "Yay!"]

def main():
    app = humanio.App(my_humanio_auth.developer_id,
                      my_humanio_auth.secret_key,
                      public=False)
    print "Connecting to the 1984 darknet listening posts...viva la resistance!"
    app.create_task(description="Shame on You!",
                    humans_per_item=-1, #humans_per_item - How many people you are requesting. Specify -1 for unlimited number
                    thumbnail="http://sukey.io/webapp/images/photo.gif",
                    human_can_do_multiple=True,
                    #auto_repeat=None,
                    #camera=True, #you need a camera for this activity! Disable for testing
                    on_connect_fn=on_connect,
                    on_submit_fn=on_submit,
                    #latitude=51.524579, longitude=-0.082312, #currently centered on London Hackspace
                    #radius_miles=10
                    )
    print "System online, standing by for field reports..."
    app.start_loop()


def on_connect(session, task, item): 
    #session.add_image(image_array[random.randint(1, len(image_array)-1)], decorated=False)
    session.add_image("http://sukey.io/webapp/images/app/sayit.png", decorated=False)
    session.add_text("Photograph acts of police brutality...Protip: Try to get badge numbers and faces.", boxed=True)
    session.add_camera_button("image")
    session.add_submit_button("Upload")

def on_submit(session, task, form_data):
    #This is called when the human submits an image, from the UI created above.

    if form_data.get("image"):
        # User did take a photo before tapping "OK".
        print "\"%s\"" % form_data["image"]
        session.clear_screen()
        session.add_text(thanks_array[random.randint(0, len(thanks_array)-1)])
	#session.add_image(thanks_image_array[random.randint(0, len(thanks_image_array)-1)])
	session.add_image("http://sukey.io/webapp/images/app/milkshake.png")
        session.dismiss(approve=True, delay_seconds=4, new_task_hashed_id=None)
    else:
        # Didn't submit a photo. Do not approve the work.
        print "Human did not take a photo. Bad human!"
        session.dismiss(approve=False)

if __name__ == "__main__":
    main()
