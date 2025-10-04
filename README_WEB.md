Play in a browser

This repository contains a small browser port of the Flappy Bird clone that uses the existing `assets/` folder.

How to run locally (PowerShell):

1. Open PowerShell and change to the project root:

```powershell
cd C:\Users\adilr\Flappy-bird
```

2. Start a simple static server (Python's built-in server):

```powershell
python -m http.server 8000
```

3. Open your browser and navigate to:

http://localhost:8000/index.html

Notes
- Audio playback may be blocked until you click the page due to browser autoplay restrictions.
- The browser version uses simple rectangle collision and reuses the `assets/sprites` and `assets/audio` files in the repo.
- If images or audio fail to load, check the browser console for more details.