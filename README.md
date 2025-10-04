# Flappy-bird-python
A basic Flappy Bird game made in Python
A basic Flappy Bird game made in Python.

Credits
- Original project / assets used by this repo were taken from: https://github.com/zhaolingzhi/FlapPyBird-master
- This fork uses the layout and assets from: https://github.com/LeonMarqs/Flappy-bird-python — thanks to the original authors for the artwork and base code.

This fork (changes in this copy)
- Adjusted audio handling and added multiple audio candidates (you can change flap / gameover sounds).
- Improved input handling (mouse clicks + keyboard) and added an on-screen instruction overlay.
- Scaled and repositioned the start message so it no longer fills the screen.
- Added a small browser-playable port (`index.html` + `js/main.js`) that reuses the `assets/` folder.

Current state
- See `image.png` for the intended layout and visuals.

Dependencies
- Python 3.8+ and `pygame` for the native version.

How to run (native Python / pygame)
1. Create and activate a virtual environment (recommended):

```powershell
cd C:\Users\adilr\Flappy-bird
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies and run:

```powershell
pip install --upgrade pip
pip install pygame
python flappy.py
```

How to run the browser version (uses the same `assets/` folder)
1. Serve the project directory and open the page in your browser:

```powershell
cd C:\Users\adilr\Flappy-bird
python -m http.server 8000
# open http://localhost:8000/index.html
```

Notes
- Browser audio may be blocked until you interact with the page due to autoplay restrictions.
- If any assets fail to load the native game prints missing files and exits — run the scripts from the project root so the `assets/` folder is found.





