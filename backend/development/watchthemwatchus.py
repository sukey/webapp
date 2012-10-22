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

watchthemwatchus is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

watchthemwatchus is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero Public License
along with watchthemwatchus.  If not, see <http://www.gnu.org/licenses/>.
'''

import humanio
import random
import my_humanio_auth
import os
"""Run a command and capture it's output string, error string and exit status"""
class Command(object):
    def __init__(self, command):
        self.command = command

    def run(self, shell=True):
        import subprocess as sp
        process = sp.Popen(self.command, shell = shell, stdout = sp.PIPE, stderr = sp.PIPE)
        self.pid = process.pid
        self.output, self.error = process.communicate()
        self.failed = process.returncode
        return self

    @property
    def returncode(self):
        return self.failed

thanks_array = ["You rock!","Thanks!", "Great Stuff!", "Merci beaucoup!", "Got it!", "Danke schon!", "Nice photo!", "Omnomnom... Photo!", "Yay!"]

def main():
    app = humanio.App(my_humanio_auth.developer_id,
                      my_humanio_auth.secret_key,
                      public=False)
    print "Connecting to the 1984 darknet listening posts...viva la resistance!"
    app.create_task(description="Watching Them, Watching Us.",
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
    session.add_image("http://sukey.io/webapp/images/watching.png", decorated=False)
    session.add_text("Watching them watching us.")
    session.add_text("Snap a pic of FIT Squads, Police with Cameras, etc. Ask them to smile!")
    session.add_camera_button("image")
    session.add_submit_button("Upload")

def on_submit(session, task, form_data):
    #This is called when the human submits an image, from the UI created above.

    if form_data.get("image"):
	#download the image
        com = Command("dd if=/dev/random count=1 | cat - %s | sha512sum - | awk -F '' '{print $1$2$3$4$5$6$7$8$9$10$11$12$13$14$15$16$17$18\".jpg\"}'").run()
        #dd if=/dev/random count=1 | cat - %s | sha512sum - | awk -F '' '{print $1$2$3$4$5$6$7$8$9$10$11$12$13$14$15$16$17$18\".jpg\"}'"
        print com.output
	#this works: wget -O d0c980c5edb23d8911.jpg http://human.io/static/images/api/nsfw-test-2.jpg
	os.system("wget -O %s %s" % (com.output, form_data["image"])) #this doesn't work. WHY!?!?!??!?!
	print "Bye bye nasty Exif Data..."
	os.system("exiftool -all= %s" % com.output) #strip the exif data
	os.system("exiftool -delete_original! %s" % com.output) #delete the backup file
	#todo use the touch command to fuxxx the timestamp (avoid leaked data of uploaded file
        session.clear_screen()
        session.add_title(thanks_array[random.randint(0, len(thanks_array)-1)])
	session.add_image("http://sukey.io/webapp/images/milkshake.png")
        session.add_text("Please remember: if you suspect it, please report it to your nearest people's movement.")
        session.dismiss(approve=True, delay_seconds=4, new_task_hashed_id=None)
	#new_task_hashed_id - The task_hashed_id for another task, as returned when that task was created. Specify this to send human to a new task after they're dismissed.
    else:
        # Clicked Ok but didn't submit a photo. Do not approve the work.
        print "Human did not take a photo. Bad human!"
        session.dismiss(approve=False)

if __name__ == "__main__":
    main()
