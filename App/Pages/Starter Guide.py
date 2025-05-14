# TODO Start guide goes here.

import streamlit as st

st.set_page_config(page_title="Starter Guide - GamesPlane")
st.header("Starter Guide")

"""
#### Welcome to GamesPlane  
Welcome to GamesPlane, GamesCrafters' AR display tool for GamesmanUni board overlays.  
I'm honored you're giving GamesPlane a try. It won't be long before you're able to have your favorite GamesCrafters games
running with Augmented Reality overlays from GamesmanUni.   
**Let's get started!**
"""

"""---"""

"""
#### Primer: What is GamesPlane?
GamesPlane is a system for rendering the move overlays you can find on GamesmanUni in AR (Augmented Reality), enabling you to see value moves
in real life. It also contains features for setting up new games with the system.  
GamesPlane makes use of ArUco markers, which are square black-and-white markers that cameras have an easy time detecting.  
"""

"""---"""

"""
#### Playing a Game
Let's learn how to play an existing game with GamesPlane. You'll need:
- A GamesPlane board and pieces. You can find them in the `GamesPlane/App/PDFs` folder. Pick a game to play and print its board and pieces out. Use 8.5x11" printer paper and black ink.
- A camera. You can connect your phone camera to your computer or use a wired webcam. Webcams built into laptops can be hard to point at the board. Place the camera on a tripod or other holder so it can see the board from the **top down**. You can also just pick it up and point it at the board whenver you want to see an overlay; it doesn't need to be perfectly still.
- The [GamesmanUni](https://github.com/GamesCrafters/GamesmanUni) repository locally.  

Now, follow these steps:
1. Check out GamesmanUni to the branch `ar/ae`. Build the site with `yarn build`.
2. Start [GamesmanUni](https://github.com/GamesCrafters/GamesmanUni) locally with `yarn dev`. Ensure it runs on localhost:3000.
3. Place the board on the table. Set up the pieces on it.
4. Point your webcam at the board.
5. Go to Launch Game. Click the game from the list.
6. Click "Activate Camera" to start your camera.
7. The screen should pop up with your camera's output. Move it around until it sees the board correctly.

At this point, it should display your AR video feed!
"""

"""
#### Troubleshooting
##### Restarting Streamlit
This tends to fix a lot of the issues I run across: End your Streamlit session with CTRL+C in the console you used to start it. Wait a moment, then start it again.  
I recommend closing old Streamlit windows as they can lag out your machine. You only need one Streamlit window open.

##### The game I want to play isn't in the list
It's possible the game simply hasn't been added to GamesPlane yet, or it wasn't added to the dictionary of games. Check with whoever added it.
##### The console says "Trying to access given camera..." a million times
This probably means your camera is in use, or hasn't yet finished up from the last time you ran the program.
1. Exit out of Streamlit with CTRL+C.
2. Close any programs that might be using your webcam, like Zoom, Google Meet, the Camera app, etc.
3. Wait 15 seconds.
4. Restart Streamlit by running the command again.
##### My video feed doesn't appear on Launch Game
Your camera is likely not being grabbed correctly because you have several cameras on your computer. Do this:
1. Go to the file `LaunchGame.py` in `App/Pages`.
2. Go to the line reading `ses.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)` (around line 46)

Now: Try changing the line to the following and rerun the page.
- **If you have a newer camera:** `ses.camera = cv2.VideoCapture(0)`
- **If you have two cameras:** `ses.camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)`
- **If you have two newer cameras:** `ses.camera = cv2.VideoCapture(1)`

##### No overlay is shown
1. **Check if it's a winning state.** Winning states don't have a GamesmanUni overlay, so nothing shows.
2. **Check that anchors and pieces are visible.** Anchors and pieces are outlined in white or yellow when detected. If they're not showing up, the game
may be set up wrong, or the camera may be out of focus.
##### The AR loading overlay turns gray
This happens when the web request fails.   
**You might be on the wrong version of GamesmanUni -- you must be on the `ae/ar` branch.** It also can happen if the yarn server is too slow.  
Try closing out of the Streamlit app, then GamesmanUni. Then restart GamesmanUni and Streamlit in that order.  
If this happens consistently and you are on the `ae/ar` branch, try this: Go to `App/BoardFetcher.py` and go to the line reading `await asyncio.sleep(2.5)`. This gives
GamesmanUni 2.5 seconds to find the overlay. Change out 2.5 for a larger number (maybe 5 seconds) to give GamesmanUni more time to create the overlay.
##### The AR output isn't correct / shows the wrong moves
1. **Check the turn.** It's possible you have the turn set wrong. Click the turn switch to change the turn.
2. **Check the ArUcos are correct.** It's possible an ArUco is the wrong ID.
3. **Check the ArUcos are the right size.** If you accidentally printed anything too large, it will likely be detected incorrectly.
4. **Straighten the camera.** The camera should be facing directly down at the board.

##### I tried everything and it still doesn't work
Let me (Miller Hollinger) know! There are a lot of moving parts in GamesPlane and I'm happy to help you fix them. You can contact me on the GamesCrafters Slack.
"""