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
