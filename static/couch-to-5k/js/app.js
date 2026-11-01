(function () {
  var plan = window.PLAN, sessions = plan.sessions;
  var STORE = 'c25k-trot-2026';
  var WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  var done = {};
  try { done = JSON.parse(localStorage.getItem(STORE) || '{}') || {}; } catch (e) { done = {}; }
  function save() { try { localStorage.setItem(STORE, JSON.stringify(done)); } catch (e) {} }

  function parse(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function iso(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function today() { var n = new Date(); return new Date(n.getFullYear(), n.getMonth(), n.getDate()); }
  function dayDiff(a, b) { return Math.round((a - b) / 86400000); }
  function total(s) { return s.segs.reduce(function (t, g) { return t + g.sec; }, 0); }
  function runTotal(s) { return s.segs.reduce(function (t, g) { return t + (g.type === 'run' ? g.sec : 0); }, 0); }
  function mmss(sec) { var m = Math.floor(sec / 60), s = sec % 60; return m + ':' + String(s).padStart(2, '0'); }
  function minLabel(sec) { return Math.round(sec / 60) + ' min'; }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

  var byDate = {};
  sessions.forEach(function (s) { byDate[s.date] = s; });

  function bar(s) {
    var b = el('div', 'seg');
    b.setAttribute('aria-hidden', 'true');
    var t = total(s);
    s.segs.forEach(function (g) {
      var i = el('i', g.type);
      i.style.flexGrow = g.sec;
      i.title = (g.type === 'run' ? 'Run ' : 'Walk ') + mmss(g.sec);
      b.appendChild(i);
    });
    return b;
  }

  // ---- summary -------------------------------------------------------
  function summary() {
    var n = sessions.filter(function (s) { return done[s.id]; }).length;
    document.getElementById('doneCount').textContent = n;
    document.getElementById('doneOf').textContent = 'of ' + sessions.length;
    var r = 52, c = 2 * Math.PI * r, bar = document.getElementById('ringBar');
    bar.style.strokeDasharray = c;
    bar.style.strokeDashoffset = c * (1 - n / sessions.length);
    document.getElementById('ring').setAttribute('aria-label', n + ' of ' + sessions.length + ' sessions completed');

    var d = dayDiff(parse(plan.raceDate), today());
    var days = document.getElementById('days'), lab = document.getElementById('daysLabel');
    if (d > 1) { days.textContent = d; lab.textContent = 'days to the Turkey Trot'; }
    else if (d === 1) { days.textContent = '1'; lab.textContent = 'day to go: shakeout day'; }
    else if (d === 0) { days.textContent = 'Today!'; lab.textContent = 'Go get it. Start slow.'; }
    else { days.textContent = 'Done'; lab.textContent = 'The Turkey Trot is behind you'; }

    var nx = document.getElementById('next'), t = iso(today());
    var up = sessions.filter(function (s) { return !done[s.id] && s.date >= t; })[0];
    nx.hidden = !up;
    if (up) {
      nx.innerHTML = '';
      var when = up.date === t ? 'Today' : (dayDiff(parse(up.date), today()) === 1 ? 'Tomorrow' : fmt(parse(up.date)));
      nx.appendChild(el('span', 'next-k', 'Next up'));
      nx.appendChild(el('strong', null, when + ': ' + up.title));
      var b = el('button', 'btn', 'Open'); b.type = 'button';
      b.addEventListener('click', function () { openDetail(up); });
      nx.appendChild(b);
    }
  }
  function fmt(d) { return WD[d.getDay()] + ', ' + MON[d.getMonth()] + ' ' + d.getDate(); }

  // ---- calendar ------------------------------------------------------
  function render() {
    var wrap = document.getElementById('weeks');
    wrap.innerHTML = '';
    var start = parse(plan.firstMonday), end = parse(plan.lastDay), t = iso(today());
    var weekNo = 0;
    for (var wk = new Date(start); wk <= end; wk.setDate(wk.getDate() + 7)) {
      weekNo++;
      var sec = el('section', 'week');
      var done7 = 0, tot7 = 0;
      var list = el('ol', 'days');
      for (var k = 0; k < 7; k++) {
        var d = new Date(wk.getFullYear(), wk.getMonth(), wk.getDate() + k);
        var key = iso(d), s = byDate[key];
        var li = el('li', 'day' + (key === t ? ' is-today' : '') + (s ? ' has-run' : ' rest'));
        li.appendChild(el('div', 'dh', '<span class="wd">' + WD[d.getDay()] + '</span><span class="dn">' + MON[d.getMonth()] + ' ' + d.getDate() + '</span>'));
        if (s) {
          tot7++;
          if (done[s.id]) { done7++; li.classList.add('is-done'); }
          else if (key < t) li.classList.add('is-missed');
          if (s.race) li.classList.add('is-race');
          var card = el('button', 'card');
          card.type = 'button';
          card.setAttribute('aria-haspopup', 'dialog');
          card.appendChild(el('strong', null, s.title));
          card.appendChild(el('span', 'meta', s.race ? '3.1 miles' : minLabel(total(s)) + ' &middot; ' + minLabel(runTotal(s)) + ' running'));
          card.appendChild(bar(s));
          (function (sx) { card.addEventListener('click', function () { openDetail(sx); }); })(s);
          li.appendChild(card);
          var chk = el('button', 'check');
          chk.type = 'button';
          chk.setAttribute('aria-pressed', done[s.id] ? 'true' : 'false');
          chk.setAttribute('aria-label', 'Mark "' + s.title + '" ' + fmt(d) + ' as done');
          chk.innerHTML = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4.5 10.5l3.5 3.5 7.5-8"/></svg>';
          (function (sx) { chk.addEventListener('click', function () { toggle(sx.id); }); })(s);
          li.appendChild(chk);
        } else if (key > plan.raceDate) {
          li.appendChild(el('span', 'restlbl', 'Recover'));
        } else {
          li.appendChild(el('span', 'restlbl', key === plan.raceDate ? '' : 'Rest'));
        }
        list.appendChild(li);
      }
      var head = el('h3', 'wh', 'Week ' + weekNo + ' <small>' + done7 + '/' + tot7 + '</small>');
      sec.appendChild(head);
      sec.appendChild(list);
      wrap.appendChild(sec);
    }
    summary();
  }

  function toggle(id) {
    if (done[id]) delete done[id]; else done[id] = true;
    save(); render();
    if (dlg.open && current && current.id === id) fillDetail(current);
  }

  // ---- detail dialog + guided timer ---------------------------------
  var dlg = document.getElementById('detail'), body = document.getElementById('detailBody'), current = null;
  var timer = null;

  function openDetail(s) {
    current = s;
    fillDetail(s);
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
  }
  dlg.addEventListener('close', function () { stopTimer(); });

  function fillDetail(s) {
    stopTimer();
    body.innerHTML = '';
    var d = parse(s.date);
    body.appendChild(el('p', 'eyebrow', fmt(d) + (s.race ? ' &middot; Race day' : ' &middot; Week ' + s.week)));
    var h = el('h2', null, s.title); h.id = 'dTitle'; body.appendChild(h);
    body.appendChild(el('p', 'meta', minLabel(total(s)) + ' total &middot; ' + minLabel(runTotal(s)) + ' of running'));
    body.appendChild(bar(s));

    var ol = el('ol', 'steps');
    s.segs.forEach(function (g) {
      ol.appendChild(el('li', g.type, '<b>' + (g.type === 'run' ? 'Run' : 'Walk') + '</b> ' + mmss(g.sec)));
    });
    body.appendChild(ol);
    body.appendChild(el('p', 'tip', s.tip));

    var act = el('div', 'actions');
    if (!s.race) {
      var start = el('button', 'btn primary', 'Start guided workout'); start.type = 'button';
      start.addEventListener('click', function () { startTimer(s); });
      act.appendChild(start);
    }
    var mark = el('button', 'btn' + (done[s.id] ? ' on' : ''), done[s.id] ? 'Done &check; (tap to undo)' : 'Mark as done'); mark.type = 'button';
    mark.addEventListener('click', function () { toggle(s.id); });
    act.appendChild(mark);
    body.appendChild(act);
    body.appendChild(el('div', 'timerbox'));
  }

  var audio = null, muted = false, wake = null;
  function beep(freq, ms) {
    if (muted) return;
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      var o = audio.createOscillator(), g = audio.createGain();
      o.frequency.value = freq; o.connect(g); g.connect(audio.destination);
      g.gain.setValueAtTime(0.0001, audio.currentTime);
      g.gain.exponentialRampToValueAtTime(0.4, audio.currentTime + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + ms / 1000);
      o.start(); o.stop(audio.currentTime + ms / 1000 + 0.05);
    } catch (e) {}
  }
  function cue(g) {
    beep(g.type === 'run' ? 880 : 520, 350);
    try { if (navigator.vibrate) navigator.vibrate(g.type === 'run' ? [200, 80, 200] : 300); } catch (e) {}
    try {
      if (!muted && window.speechSynthesis) {
        var u = new SpeechSynthesisUtterance(g.type === 'run' ? 'Run' : 'Walk');
        speechSynthesis.cancel(); speechSynthesis.speak(u);
      }
    } catch (e) {}
  }

  function startTimer(s) {
    var box = body.querySelector('.timerbox');
    box.innerHTML = '';
    var label = el('div', 'tlabel', ''), clock = el('div', 'tclock', ''), nextl = el('div', 'tnext', '');
    var ctl = el('div', 'actions');
    var pause = el('button', 'btn', 'Pause'); pause.type = 'button';
    var skip = el('button', 'btn', 'Skip'); skip.type = 'button';
    var mute = el('button', 'btn', muted ? 'Sound off' : 'Sound on'); mute.type = 'button';
    ctl.appendChild(pause); ctl.appendChild(skip); ctl.appendChild(mute);
    box.appendChild(label); box.appendChild(clock); box.appendChild(nextl); box.appendChild(ctl);
    box.className = 'timerbox live';

    var idx = 0, left = s.segs[0].sec, paused = false, last = Date.now();
    try { if (navigator.wakeLock) navigator.wakeLock.request('screen').then(function (w) { wake = w; }).catch(function () {}); } catch (e) {}
    function paint() {
      var g = s.segs[idx];
      box.dataset.type = g.type;
      label.textContent = g.type === 'run' ? 'RUN' : 'WALK';
      clock.textContent = mmss(Math.max(0, Math.ceil(left)));
      var nx = s.segs[idx + 1];
      nextl.textContent = nx ? 'Next: ' + (nx.type === 'run' ? 'run ' : 'walk ') + mmss(nx.sec) + '  ·  ' + (idx + 1) + ' of ' + s.segs.length : 'Last one: ' + (idx + 1) + ' of ' + s.segs.length;
    }
    function advance() {
      idx++;
      if (idx >= s.segs.length) {
        stopTimer(); beep(660, 250); setTimeout(function () { beep(880, 500); }, 300);
        box.className = 'timerbox finished';
        box.innerHTML = '<strong>Nice work.</strong> Session complete.';
        if (!done[s.id]) { done[s.id] = true; save(); render(); fillDoneOnly(); }
        return;
      }
      left = s.segs[idx].sec; cue(s.segs[idx]); paint();
    }
    function fillDoneOnly() {
      var b = body.querySelector('.actions .btn:not(.primary)');
      if (b) { b.className = 'btn on'; b.innerHTML = 'Done &check; (tap to undo)'; }
    }
    pause.addEventListener('click', function () { paused = !paused; pause.textContent = paused ? 'Resume' : 'Pause'; last = Date.now(); });
    skip.addEventListener('click', advance);
    mute.addEventListener('click', function () { muted = !muted; mute.textContent = muted ? 'Sound off' : 'Sound on'; if (muted && window.speechSynthesis) speechSynthesis.cancel(); });
    cue(s.segs[0]); paint();
    timer = setInterval(function () {
      var now = Date.now(), dt = (now - last) / 1000; last = now;
      if (paused) return;
      left -= dt;
      if (left <= 0) advance(); else paint();
    }, 250);
  }
  function stopTimer() {
    if (timer) { clearInterval(timer); timer = null; }
    try { if (wake) { wake.release(); wake = null; } } catch (e) {}
    try { if (window.speechSynthesis) speechSynthesis.cancel(); } catch (e) {}
  }

  document.getElementById('reset').addEventListener('click', function () {
    if (confirm('Clear all checked-off sessions?')) { done = {}; save(); render(); }
  });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });

  render();
  requestAnimationFrame(function () { document.getElementById('ring').classList.add('ready'); });
})();
