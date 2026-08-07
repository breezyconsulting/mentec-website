// Safety net: [data-reveal] elements default to opacity:0 until JS adds 'in'.
// If anything below throws, force them visible after a short delay so a
// script error can never blank the page.
setTimeout(function(){
  document.querySelectorAll('[data-reveal]:not(.in)').forEach(function(el){ el.classList.add('in'); });
}, 1200);

(function(){
  // reveal-on-scroll
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function(entries){
    entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {threshold:0.12}) : null;
  document.querySelectorAll('[data-reveal]').forEach(function(el){
    if(io){ io.observe(el); } else { el.classList.add('in'); }
  });

  // count-up numbers (e.g. "80%") — markup already has the real final value,
  // so no-JS/crawlers see it as-is; this just animates 0 -> value on reveal.
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function animateCountUp(el){
    var target = parseFloat(el.getAttribute('data-countup'));
    var suffix = el.getAttribute('data-suffix') || '';
    var decimals = (el.getAttribute('data-countup').split('.')[1] || '').length;
    if(reduceMotion || isNaN(target)){ el.textContent = target.toFixed(decimals) + suffix; return; }
    var duration = 1400, start = null;
    function tick(ts){
      if(start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3); // ease-out-cubic
      el.textContent = (target * eased).toFixed(decimals) + suffix;
      if(p < 1) requestAnimationFrame(tick); else el.textContent = target.toFixed(decimals) + suffix;
    }
    requestAnimationFrame(tick);
  }
  var countEls = document.querySelectorAll('[data-countup]');
  var countIo = ('IntersectionObserver' in window) ? new IntersectionObserver(function(entries){
    entries.forEach(function(e){ if(e.isIntersecting){ animateCountUp(e.target); countIo.unobserve(e.target); } });
  }, {threshold:0.5}) : null;
  countEls.forEach(function(el){ if(countIo){ countIo.observe(el); } });

  // impact chart: draw-in animation + hover tooltip/crosshair
  document.querySelectorAll('.chart-card').forEach(function(card){
    var drawn = false;
    function draw(){
      if(drawn) return;
      drawn = true;
      var paths = card.querySelectorAll('.chart-line');
      if(reduceMotion){ card.classList.add('drawn', 'no-anim'); return; }
      paths.forEach(function(path){
        var len = path.getTotalLength();
        path.style.strokeDasharray = len;
        path.style.strokeDashoffset = len;
        path.getBoundingClientRect(); // force reflow so the transition catches the offset change
        requestAnimationFrame(function(){ path.style.strokeDashoffset = 0; });
      });
      card.classList.add('drawn');
    }
    if('IntersectionObserver' in window){
      var cio = new IntersectionObserver(function(entries){
        entries.forEach(function(e){ if(e.isIntersecting){ draw(); cio.unobserve(e.target); } });
      }, {threshold:0.35});
      cio.observe(card);
    } else { draw(); }

    var svg = card.querySelector('.chart-svg');
    if(!svg) return;
    var raw = svg.getAttribute('data-chart');
    if(!raw) return;
    var data = JSON.parse(raw);
    var wrap = card.querySelector('.chart-svg-wrap');
    var tooltip = card.querySelector('.chart-tooltip');
    var crosshair = svg.querySelector('.chart-crosshair');
    var hoverDots = {};
    svg.querySelectorAll('.chart-hover-dot').forEach(function(d){ hoverDots[d.getAttribute('data-series')] = d; });

    function yFor(v){
      var t = (v - data.ymin) / (data.ymax - data.ymin);
      return data.y1 - t * (data.y1 - data.y0);
    }
    function xFor(i){ return data.x0 + (i / (data.months.length - 1)) * (data.x1 - data.x0); }

    function move(clientX, clientY){
      var rect = svg.getBoundingClientRect();
      var localX = clientX - rect.left;
      if(localX < 0 || localX > rect.width){ leave(); return; }
      var vx = (localX / rect.width) * data.vw;
      var frac = (vx - data.x0) / (data.x1 - data.x0);
      var idx = Math.round(frac * (data.months.length - 1));
      idx = Math.max(0, Math.min(data.months.length - 1, idx));
      var mx = xFor(idx);
      crosshair.setAttribute('x1', mx); crosshair.setAttribute('x2', mx);
      crosshair.style.opacity = 1;
      var rows = '';
      data.series.forEach(function(s){
        var v = s.values[idx];
        var dot = hoverDots[s.id];
        if(dot){ dot.setAttribute('cx', mx); dot.setAttribute('cy', yFor(v)); dot.style.opacity = 1; }
        rows += '<div class="tt-row"><span>' + s.label.replace(' (indexed)','') + '</span><b class="tabular">' + v + '</b></div>';
      });
      tooltip.innerHTML = '<span class="tt-month">Month ' + idx + '</span>' + rows;
      tooltip.hidden = false;
      tooltip.classList.add('visible');
      var wrapRect = wrap.getBoundingClientRect();
      tooltip.style.left = (clientX - wrapRect.left) + 'px';
      tooltip.style.top = (rect.top - wrapRect.top + (yFor(data.series[1].values[idx]) / data.vh) * rect.height) + 'px';
    }
    function leave(){
      crosshair.style.opacity = 0;
      Object.keys(hoverDots).forEach(function(k){ hoverDots[k].style.opacity = 0; });
      tooltip.classList.remove('visible');
      tooltip.hidden = true;
    }
    wrap.addEventListener('pointermove', function(e){ move(e.clientX, e.clientY); });
    wrap.addEventListener('pointerleave', leave);
  });

  // mega nav (Company dropdown)
  var navItems = document.querySelectorAll('.navitem[data-group]');
  function closeMega(){
    navItems.forEach(function(it){
      it.querySelector('.navbtn').setAttribute('aria-expanded','false');
      it.querySelector('.mega').classList.remove('open');
    });
  }
  navItems.forEach(function(item){
    var btn = item.querySelector('.navbtn');
    var mega = item.querySelector('.mega');
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      var isOpen = mega.classList.contains('open');
      closeMega();
      if(!isOpen){ mega.classList.add('open'); btn.setAttribute('aria-expanded','true'); }
    });
  });
  document.addEventListener('click', closeMega);

  // mobile panel
  var mobileToggle = document.getElementById('mobileToggle');
  var mobilePanel = document.getElementById('mobilePanel');
  function closeMobile(){ mobilePanel.classList.remove('open'); mobileToggle.setAttribute('aria-expanded','false'); }
  if(mobileToggle && mobilePanel){
    mobileToggle.addEventListener('click', function(e){
      e.stopPropagation();
      var open = mobilePanel.classList.toggle('open');
      mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  document.addEventListener('keydown', function(e){ if(e.key === 'Escape'){ closeMega(); closeMobile(); } });

  // stop nav link clicks bubbling to the document-level closeMega handler
  document.querySelectorAll('.mega-link, .mobile-panel a').forEach(function(a){
    a.addEventListener('click', function(e){ e.stopPropagation(); });
  });
})();
