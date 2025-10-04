(function(){
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  // asset paths (reuse your assets folder)
  const paths = {
    bg: 'assets/sprites/background-day.png',
    base: 'assets/sprites/base.png',
    msg: 'assets/sprites/message.png',
    pipe: 'assets/sprites/pipe-green.png',
    bird0: 'assets/sprites/bluebird-upflap.png',
    bird1: 'assets/sprites/bluebird-midflap.png',
    bird2: 'assets/sprites/bluebird-downflap.png'
  };

  // candidate audio files (will be loaded if present)
  const flapCandidates = [
    'assets/audio/wing.wav',
    'assets/audio/wing.ogg',
    'assets/audio/wing.mp3',
    'assets/audio/swoosh.wav',
    'assets/audio/swoosh.ogg'
  ];
  const gameoverCandidates = [
    'assets/audio/hit.wav',
    'assets/audio/hit.ogg',
    'assets/audio/die.wav',
    'assets/audio/die.ogg',
    'assets/audio/swoosh.wav',
    'assets/audio/swoosh.ogg'
  ];

  function loadImage(src){
    return new Promise((res, rej)=>{
      const i = new Image();
      i.onload = ()=>res(i);
      i.onerror = ()=>rej(new Error('Failed to load '+src));
      i.src = src;
    });
  }
  function loadAudio(src){
    return new Promise((res)=>{
      const a = new Audio();
      a.src = src;
      a.oncanplaythrough = ()=>res(a);
      a.onerror = ()=>res(null); // audio may be blocked or fail
    });
  }

  // Preload images first
  Promise.all([
    loadImage(paths.bg),
    loadImage(paths.base),
    loadImage(paths.msg),
    loadImage(paths.pipe),
    loadImage(paths.bird0),
    loadImage(paths.bird1),
    loadImage(paths.bird2)
  ]).then(images=>{
    const [BG, BASE, MSG, PIPE, B0, B1, B2] = images;

    // Try to load candidate audio files (some may return null)
    Promise.all([
      Promise.all(flapCandidates.map(p=>loadAudio(p))),
      Promise.all(gameoverCandidates.map(p=>loadAudio(p)))
    ]).then(([flapLoaded, gameoverLoaded])=>{
      // pick only the loaded (non-null) ones
      const flapSounds = flapCandidates.map((p,i)=>({path:p,a:flapLoaded[i]})).filter(x=>x.a);
      const gameoverSounds = gameoverCandidates.map((p,i)=>({path:p,a:gameoverLoaded[i]})).filter(x=>x.a);

      // default indexes
      let flapIndex = 0;
      let gameoverIndex = 0;

      // fallback: if none loaded, set arrays to empty
      // selected audio objects
      function currentFlap(){ return flapSounds.length? flapSounds[flapIndex].a : null }
      function currentGameover(){ return gameoverSounds.length? gameoverSounds[gameoverIndex].a : null }

      // Game state
      const STATE = { START:0, PLAY:1, GAMEOVER:2 };
      let state = STATE.START;

      // Bird
      const bird = {
        x: Math.floor(W/6),
        y: Math.floor(H/2),
        w: B0.width,
        h: B0.height,
        vy: 0,
        frame:0,
        animTimer:0,
        update(dt){
          this.animTimer += dt;
          if(this.animTimer > 100){ this.animTimer = 0; this.frame = (this.frame+1)%3 }
          if(state===STATE.PLAY){
            this.vy += 0.25 * dt/16; // gravity scaled
            this.y += this.vy * dt/16;
            if(this.y + this.h > H - GROUND_H){ this.y = H - GROUND_H - this.h; }
          }
        },
        draw(){
          const img = this.frame===0?B0:(this.frame===1?B1:B2);
          ctx.drawImage(img, this.x, this.y);
          // debug rectangle
          ctx.strokeStyle = 'red'; ctx.lineWidth=2;
          ctx.strokeRect(this.x, this.y, this.w, this.h);
        },
        flap(){ this.vy = -6; const a = currentFlap(); if(a){ try{ a.currentTime = 0 }catch(e){}; a.play().catch(()=>{}); } }
      };

      // Ground
      const GROUND_H = 100;
      let groundX = 0;

      // Pipes
      const PIPE_W = 80;
      const PIPE_H = 500;
      const PIPE_GAP = 150;
      const pipes = [];
      let spawnTimer = 0;

      function spawnPipes(){
        const size = Math.floor(100 + Math.random()*200);
        // bottom pipe
        pipes.push({x: W, y: H - size, w: PIPE_W, h: size, inv:false});
        // top (inverted)
        pipes.push({x: W, y: - (PIPE_H - (H - size - PIPE_GAP)), w: PIPE_W, h: PIPE_H, inv:true});
      }

      // collision: simple AABB
      function collide(a,b){
        return !(a.x+a.w < b.x || a.x > b.x+b.w || a.y+a.h < b.y || a.y > b.y+b.h);
      }

      // Input
      function onFlap(){
        if(state===STATE.START){ state = STATE.PLAY; bird.flap(); }
        else if(state===STATE.PLAY){ bird.flap(); }
        else if(state===STATE.GAMEOVER){ reset(); state = STATE.START; }
      }
      window.addEventListener('keydown', e=>{
        if(e.code==='Space' || e.code==='ArrowUp'){ onFlap(); }
        // cycle flap sound
        if(e.code==='Digit1'){
          if(flapSounds.length){ flapIndex = (flapIndex + 1) % flapSounds.length; const a = currentFlap(); if(a){ try{ a.currentTime = 0 }catch(e){}; a.play().catch(()=>{}); } }
        }
        // cycle gameover sound
        if(e.code==='Digit2'){
          if(gameoverSounds.length){ gameoverIndex = (gameoverIndex + 1) % gameoverSounds.length; const a = currentGameover(); if(a){ try{ a.currentTime = 0 }catch(e){}; a.play().catch(()=>{}); } }
        }
      });
      canvas.addEventListener('mousedown', e=>{ onFlap(); });

      // Reset
      function reset(){
        bird.y = H/2; bird.vy=0; bird.frame=0; pipes.length=0; spawnTimer=0; groundX=0;
      }

      // Main loop
      let last = performance.now();
      function loop(now){
        const dt = now - last; last = now;

        // update
        if(state===STATE.PLAY){
          spawnTimer += dt;
          if(spawnTimer > 1500){ spawnTimer = 0; spawnPipes(); }
          for(let i=pipes.length-1;i>=0;i--){
            pipes[i].x -= 2 * dt/16 * 4; // speed
            if(pipes[i].x + pipes[i].w < -50) pipes.splice(i,1);
          }
          groundX = (groundX - 2 * dt/16 * 4) % W;
        }

        bird.update(dt);

        // collisions
        if(state===STATE.PLAY){
          for(const p of pipes){ if(collide(bird,p)){ state = STATE.GAMEOVER; const a = currentGameover(); if(a){ try{ a.currentTime = 0 }catch(e){}; a.play().catch(()=>{}); } } }
          // ground collision
          if(bird.y + bird.h >= H - GROUND_H){ state = STATE.GAMEOVER; const a = currentGameover(); if(a){ try{ a.currentTime = 0 }catch(e){}; a.play().catch(()=>{}); } }
        }

        // draw
        // background
        ctx.drawImage(BG, 0, 0, W, H);

        // pipes
        for(const p of pipes){
          if(p.inv){
            // inverted pipe, flip vertically
            ctx.save();
            ctx.translate(p.x + p.w/2, p.y + p.h/2);
            ctx.scale(1,-1);
            ctx.drawImage(PIPE, -p.w/2, -p.h/2, p.w, p.h);
            ctx.restore();
          } else {
            ctx.drawImage(PIPE, p.x, p.y, p.w, p.h);
          }
        }

        // base (repeat)
        const baseScale = GROUND_H / BASE.height;
        const baseW = BASE.width * baseScale;
        for(let bx = groundX - baseW; bx < W + baseW; bx += baseW){
          ctx.drawImage(BASE, bx, H - GROUND_H, baseW, GROUND_H);
        }

        // bird
        bird.draw();

        // UI
        ctx.fillStyle = 'white'; ctx.font = '14px sans-serif';
        if(state===STATE.START){
          // message image centered
          const mx = (W - MSG.width)/2;
          ctx.drawImage(MSG, mx, 150);
          ctx.fillText('Click or press Space to start', 10, 20);
        } else if(state===STATE.GAMEOVER){
          ctx.fillText('Game Over - click to restart', 10,20);
        } else {
          ctx.fillText('Press Space / Click to flap', 10,20);
        }

        // audio selection UI
        ctx.font = '12px sans-serif';
        ctx.fillStyle = '#fff';
        const flapName = flapSounds.length? flapSounds[flapIndex].path.split('/').pop() : 'none';
        const goName = gameoverSounds.length? gameoverSounds[gameoverIndex].path.split('/').pop() : 'none';
        ctx.fillText('Flap sound (press 1): ' + flapName, 10, H - 40);
        ctx.fillText('Gameover sound (press 2): ' + goName, 10, H - 22);

        requestAnimationFrame(loop);
      }

      reset();
      requestAnimationFrame(loop);

    }).catch(err=>{
      console.warn('Audio load error (non fatal):', err);
      // proceed without audio
    });

  }).catch(err=>{
    console.error('Failed to load assets:', err);
    ctx.fillStyle='#000'; ctx.fillRect(0,0,W,H);
    ctx.fillStyle='#fff'; ctx.fillText('Failed to load assets. Check console.', 10,20);
  });
})();