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
  function animateNumber(target, duration, onFrame){
    if(reduceMotion || isNaN(target)){ onFrame(target); return; }
    var start = null;
    function tick(ts){
      if(start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3); // ease-out-cubic
      onFrame(target * eased, p);
      if(p < 1) requestAnimationFrame(tick); else onFrame(target, 1);
    }
    requestAnimationFrame(tick);
  }
  function animateCountUp(el){
    var target = parseFloat(el.getAttribute('data-countup'));
    var suffix = el.getAttribute('data-suffix') || '';
    var decimals = (el.getAttribute('data-countup').split('.')[1] || '').length;
    animateNumber(target, 1400, function(v){ el.textContent = v.toFixed(decimals) + suffix; });
  }
  var countEls = document.querySelectorAll('[data-countup]');
  var countIo = ('IntersectionObserver' in window) ? new IntersectionObserver(function(entries){
    entries.forEach(function(e){ if(e.isIntersecting){ animateCountUp(e.target); countIo.unobserve(e.target); } });
  }, {threshold:0.5}) : null;
  countEls.forEach(function(el){ if(countIo){ countIo.observe(el); } });

  // impact chart: draw-in animation (a "pen tip" leads each line, area fills
  // wipe in sync), animated end-labels, a "live" ping once drawn, hover
  // tooltip/crosshair, and an interactive legend (hover to spotlight a
  // series, click to toggle it off).
  document.querySelectorAll('.chart-card').forEach(function(card){
    var svg = card.querySelector('.chart-svg');
    if(!svg) return;
    var raw = svg.getAttribute('data-chart');
    if(!raw) return;
    var data = JSON.parse(raw);
    var DRAW_MS = 1500, STAGGER_MS = 220;

    var series = ['revenue', 'profit', 'cost'];
    var xSpan = data.x1 - data.x0;
    var maxDelay = (series.length - 1) * STAGGER_MS;
    var runId = 0; // bumped on every (re)draw so stale rAF loops from a
                   // previous run (e.g. scrolled away mid-animation) stop
                   // themselves instead of fighting the new one.

    function reset(){
      card.classList.remove('drawn', 'no-anim', 'pinging');
      series.forEach(function(id){
        var path = svg.querySelector('.chart-line[data-series="' + id + '"]');
        var tip = svg.querySelector('.chart-tip[data-series="' + id + '"]');
        var clipRect = svg.querySelector('.chart-clip-rect[data-series="' + id + '"]');
        var dot = svg.querySelector('.chart-dot[data-series="' + id + '"]');
        var label = svg.querySelector('.chart-endlabel[data-series="' + id + '"]');
        if(path && path.style.strokeDasharray){ path.style.strokeDashoffset = path.style.strokeDasharray; }
        if(tip) tip.style.opacity = 0;
        if(clipRect) clipRect.setAttribute('width', '0');
        if(dot) dot.classList.remove('revealed');
        if(label) label.classList.remove('revealed');
      });
    }

    function revealSeries(id){
      var dot = svg.querySelector('.chart-dot[data-series="' + id + '"]');
      var label = svg.querySelector('.chart-endlabel[data-series="' + id + '"]');
      if(dot) dot.classList.add('revealed');
      if(label) label.classList.add('revealed');
      var pct = label && label.querySelector('.chart-endlabel-pct[data-countup-pct]');
      if(pct){
        var target = parseFloat(pct.getAttribute('data-countup-pct'));
        animateNumber(target, reduceMotion ? 0 : 550, function(v){
          pct.textContent = (v >= 0 ? '+' : '') + Math.round(v) + '%';
        });
      }
    }

    function draw(){
      reset();
      var myRun = ++runId;

      if(reduceMotion){
        card.classList.add('drawn', 'no-anim');
        svg.querySelectorAll('.chart-clip-rect').forEach(function(r){ r.setAttribute('width', xSpan); });
        series.forEach(revealSeries);
      } else {
        card.classList.add('drawn');
        series.forEach(function(id, i){
          var path = svg.querySelector('.chart-line[data-series="' + id + '"]');
          var tip = svg.querySelector('.chart-tip[data-series="' + id + '"]');
          var clipRect = svg.querySelector('.chart-clip-rect[data-series="' + id + '"]');
          if(!path) return;
          var len = path.getTotalLength();
          path.style.strokeDasharray = len;
          path.style.strokeDashoffset = len;
          setTimeout(function(){
            if(myRun !== runId) return; // superseded by a later draw() before this stagger fired
            if(tip) tip.style.opacity = 1;
            var start = null;
            function tick(ts){
              if(myRun !== runId) return; // scrolled away / re-triggered mid-flight
              if(start === null) start = ts;
              var p = Math.min((ts - start) / DRAW_MS, 1);
              var eased = 1 - Math.pow(1 - p, 3); // ease-out-cubic
              path.style.strokeDashoffset = String(len * (1 - eased));
              if(tip){
                var pt = path.getPointAtLength(len * eased);
                tip.setAttribute('cx', pt.x);
                tip.setAttribute('cy', pt.y);
              }
              if(clipRect) clipRect.setAttribute('width', String(eased * xSpan));
              if(p < 1){ requestAnimationFrame(tick); }
              else {
                if(tip) tip.style.opacity = 0;
                revealSeries(id);
              }
            }
            requestAnimationFrame(tick);
          }, i * STAGGER_MS);
        });
      }
      // start the "live" ping once the slowest line has finished drawing
      setTimeout(function(){ if(myRun === runId) card.classList.add('pinging'); }, reduceMotion ? 0 : DRAW_MS + maxDelay);
    }
    if('IntersectionObserver' in window){
      var cio = new IntersectionObserver(function(entries){
        entries.forEach(function(e){ if(e.isIntersecting){ draw(); } });
      }, {threshold:0.3});
      cio.observe(card);
    } else { draw(); }

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
        var isHidden = hiddenSeries[s.id];
        if(dot){ dot.setAttribute('cx', mx); dot.setAttribute('cy', yFor(v)); dot.style.opacity = isHidden ? 0 : 1; }
        if(isHidden) return;
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

    // interactive legend — hover to spotlight one series, click to toggle it off
    var hiddenSeries = {};
    var seriesEls = {};
    data.series.forEach(function(s){
      seriesEls[s.id] = {
        line: svg.querySelector('.chart-line[data-series="' + s.id + '"]'),
        area: svg.querySelector('.chart-area[data-series="' + s.id + '"]'),
        dot: svg.querySelector('.chart-dot[data-series="' + s.id + '"]'),
        ping: svg.querySelector('.chart-ping[data-series="' + s.id + '"]'),
        label: svg.querySelector('.chart-endlabel[data-series="' + s.id + '"]'),
      };
    });
    function spotlight(id){
      Object.keys(seriesEls).forEach(function(k){
        var els = seriesEls[k];
        var on = (k === id);
        if(els.line) els.line.classList.toggle('spotlight', on && !hiddenSeries[k]);
        if(els.line) els.line.classList.toggle('dim', !on && !hiddenSeries[k]);
        if(els.dot) els.dot.classList.toggle('spotlight', on && !hiddenSeries[k]);
        if(els.dot) els.dot.classList.toggle('dim', !on && !hiddenSeries[k]);
        if(els.area) els.area.classList.toggle('dim', !on && !hiddenSeries[k]);
        if(els.label) els.label.classList.toggle('dim', !on && !hiddenSeries[k]);
      });
    }
    function clearSpotlight(){
      Object.keys(seriesEls).forEach(function(k){
        var els = seriesEls[k];
        [els.line, els.dot, els.area, els.label].forEach(function(el){ if(el) el.classList.remove('spotlight','dim'); });
      });
    }
    card.querySelectorAll('.chart-legend-item').forEach(function(btn){
      var id = btn.getAttribute('data-series');
      btn.addEventListener('mouseenter', function(){ if(!hiddenSeries[id]) spotlight(id); });
      btn.addEventListener('focus', function(){ if(!hiddenSeries[id]) spotlight(id); });
      btn.addEventListener('mouseleave', clearSpotlight);
      btn.addEventListener('blur', clearSpotlight);
      btn.addEventListener('click', function(){
        hiddenSeries[id] = !hiddenSeries[id];
        var els = seriesEls[id];
        [els.line, els.dot, els.area, els.ping, els.label].forEach(function(el){ if(el) el.classList.toggle('hidden', hiddenSeries[id]); });
        btn.classList.toggle('muted', hiddenSeries[id]);
        btn.setAttribute('aria-pressed', hiddenSeries[id] ? 'true' : 'false');
        clearSpotlight();
      });
    });
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
