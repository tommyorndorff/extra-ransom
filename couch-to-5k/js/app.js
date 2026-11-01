(function () {
  var WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var LEVEL_NAMES = { beginner: 'Starting from the couch', intermediate: 'Can run ~5 minutes', runner: 'Already running 20+ min' };

  var store, sessions = [], byDate = {}, current = null, timer = null;

  function parse(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function iso(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function today() { var n = new Date(); return new Date(n.getFullYear(), n.getMonth(), n.getDate()); }
  function dayDiff(a, b) { return Math.round((a - b) / 86400000); }
  function total(s) { return s.segs.reduce(function (t, g) { return t + g.sec; }, 0); }
  function runTotal(s) { return s.segs.reduce(function (t, g) { return t + (g.type === 'run' ? g.sec : 0); }, 0); }
  function mmss(sec) { var m = Math.floor(sec / 60), s = sec % 60; return m + ':' + String(s).padStart(2, '0'); }
  function minLabel(sec) { return Math.round(sec / 60) + ' min'; }
  function fmt(d) { return WD[d.getDay()] + ', ' + MON[d.getMonth()] + ' ' + d.getDate(); }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function done(id) { return !!store.entries[id]; }
  function logLine(e) {
    var parts = [];
    if (e.distance_mi != null) parts.push(+(+e.distance_mi).toFixed(2) + ' mi');
    if (e.duration_min != null) parts.push(+(+e.duration_min).toFixed(1) + ' min');
    if (e.run_pct != null) parts.push(e.run_pct + '% run');
    return parts.join(' · ');
  }

  function bar(s) {
    var b = el('div', 'seg');
    b.setAttribute('aria-hidden', 'true');
    s.segs.forEach(function (g) {
      var i = el('i', g.type);
      i.style.flexGrow = g.sec;
      i.title = (g.type === 'run' ? 'Run ' : 'Walk ') + mmss(g.sec);
      b.appendChild(i);
    });
    return b;
  }

  // ---- header ---------------------------------------------------------
  function banner(msg) {
    var b = document.getElementById('banner');
    b.hidden = !msg; b.textContent = msg || '';
  }
  function who() {
    var w = document.getElementById('who');
    w.hidden = false;
    var name = document.getElementById('whoName'), note = document.getElementById('whoNote'), sel = document.getElementById('levelSel');
    sel.innerHTML = '';
    PLAN.levels.forEach(function (l) { var o = el('option', null, esc(LEVEL_NAMES[l])); o.value = l; sel.appendChild(o); });
    sel.value = store.level;
    sel.disabled = !store.canEdit;
    var link = document.getElementById('summaryLink');
    if (store.mode === 'remote') {
      var dot = document.getElementById('whoDot'); dot.hidden = false; dot.style.background = store.color;
      if (store.canEdit) colorPicker();
      name.textContent = store.name + (store.canEdit ? '' : ' (view only)');
      link.href = 'summary/?p=' + encodeURIComponent(store.token);
      note.textContent = store.canEdit ? 'Your log is saved to the shared server. Keep this link private: anyone with it can edit your log.' : 'This is a read-only link.';
      document.getElementById('saveNote').textContent = 'Saved to the server for ' + store.name + '.';
      document.getElementById('reset').hidden = true;
    } else {
      name.textContent = 'Just you, on this device';
      link.href = 'summary/';
      note.textContent = 'Saved in this browser only. Ask for a personal link to keep your log across devices.';
    }
    sel.onchange = function () {
      var lvl = sel.value;
      store.setLevel(lvl).then(function () { reload(); }).catch(function () { sel.value = store.level; banner('Could not save the plan level. Try again.'); });
    };
  }

  // Color swatches plus a free color input. Changing it updates the dot others see on the team page.
  function colorPicker() {
    document.getElementById('colorRow').hidden = false;
    var box = document.getElementById('swatches'); box.innerHTML = '';
    function choose(c) {
      store.setColor(c).then(function () { banner(''); paint(); }).catch(function () { banner('Could not save your color. Try again.'); });
    }
    function paint() {
      document.getElementById('whoDot').style.background = store.color;
      Array.prototype.forEach.call(box.querySelectorAll('button'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.c === store.color)); });
      custom.value = store.color;
    }
    C25K.palette.forEach(function (c) {
      var b = el('button', 'sw-btn'); b.type = 'button'; b.dataset.c = c; b.style.background = c; b.setAttribute('aria-label', 'Use color ' + c);
      b.addEventListener('click', function () { choose(c); });
      box.appendChild(b);
    });
    var custom = el('input', 'sw-custom'); custom.type = 'color'; custom.setAttribute('aria-label', 'Pick any color');
    custom.addEventListener('change', function () { choose(custom.value.toLowerCase()); });
    box.appendChild(custom);
    paint();
  }

  function reload() {
    sessions = PLAN.sessionsFor(store.level);
    byDate = {};
    sessions.forEach(function (s) { byDate[s.date] = s; });
    render();
  }

  // ---- summary strip --------------------------------------------------
  function summary() {
    var n = sessions.filter(function (s) { return done(s.id); }).length;
    document.getElementById('doneCount').textContent = n;
    document.getElementById('doneOf').textContent = 'of ' + sessions.length;
    var r = 52, c = 2 * Math.PI * r, ring = document.getElementById('ringBar');
    ring.style.strokeDasharray = c;
    ring.style.strokeDashoffset = c * (1 - n / sessions.length);
    document.getElementById('ring').setAttribute('aria-label', n + ' of ' + sessions.length + ' sessions completed');

    var d = dayDiff(parse(PLAN.raceDate), today());
    var days = document.getElementById('days'), lab = document.getElementById('daysLabel');
    if (d > 1) { days.textContent = d; lab.textContent = 'days to the Turkey Trot'; }
    else if (d === 1) { days.textContent = '1'; lab.textContent = 'day to go: shakeout day'; }
    else if (d === 0) { days.textContent = 'Today!'; lab.textContent = 'Go get it. Start slow.'; }
    else { days.textContent = 'Done'; lab.textContent = 'The Turkey Trot is behind you'; }

    var nx = document.getElementById('next'), t = iso(today());
    var up = sessions.filter(function (s) { return !done(s.id) && s.date >= t; })[0];
    nx.hidden = !up;
    if (up) {
      nx.innerHTML = '';
      var when = up.date === t ? 'Today' : (dayDiff(parse(up.date), today()) === 1 ? 'Tomorrow' : fmt(parse(up.date)));
      nx.appendChild(el('span', 'next-k', 'Next up'));
      nx.appendChild(el('strong', null, esc(when + ': ' + up.title)));
      var b = el('button', 'btn', 'Open'); b.type = 'button';
      b.addEventListener('click', function () { openDetail(up); });
      nx.appendChild(b);
    }
  }

  // ---- calendar -------------------------------------------------------
  function render() {
    var wrap = document.getElementById('weeks');
    wrap.innerHTML = '';
    var start = parse(PLAN.firstMonday), end = parse(PLAN.lastDay), t = iso(today()), weekNo = 0;
    for (var wk = new Date(start); wk <= end; wk.setDate(wk.getDate() + 7)) {
      weekNo++;
      var sec = el('section', 'week'), done7 = 0, tot7 = 0, list = el('ol', 'days');
      for (var k = 0; k < 7; k++) {
        var d = new Date(wk.getFullYear(), wk.getMonth(), wk.getDate() + k);
        var key = iso(d), s = byDate[key];
        var li = el('li', 'day' + (key === t ? ' is-today' : '') + (s ? ' has-run' : ' rest'));
        li.appendChild(el('div', 'dh', '<span class="wd">' + WD[d.getDay()] + '</span><span class="dn">' + MON[d.getMonth()] + ' ' + d.getDate() + '</span>'));
        if (s) {
          tot7++;
          if (done(s.id)) { done7++; li.classList.add('is-done'); }
          else if (key < t) li.classList.add('is-missed');
          if (s.race) li.classList.add('is-race');
          var card = el('button', 'card');
          card.type = 'button';
          card.setAttribute('aria-haspopup', 'dialog');
          card.appendChild(el('strong', null, esc(s.title)));
          var meta = s.race ? '3.1 miles' : minLabel(total(s)) + ' &middot; ' + minLabel(runTotal(s)) + ' running';
          card.appendChild(el('span', 'meta', meta));
          if (done(s.id) && logLine(store.entries[s.id])) card.appendChild(el('span', 'logged', esc(logLine(store.entries[s.id]))));
          card.appendChild(bar(s));
          (function (sx) { card.addEventListener('click', function () { openDetail(sx); }); })(s);
          li.appendChild(card);
          var chk = el('button', 'check');
          chk.type = 'button';
          chk.disabled = !store.canEdit;
          chk.setAttribute('aria-pressed', done(s.id) ? 'true' : 'false');
          chk.setAttribute('aria-label', 'Mark ' + s.title + ', ' + fmt(d) + ', as done');
          chk.innerHTML = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4.5 10.5l3.5 3.5 7.5-8"/></svg>';
          (function (sx) { chk.addEventListener('click', function () { quickToggle(sx); }); })(s);
          li.appendChild(chk);
        } else if (key > PLAN.raceDate) {
          li.appendChild(el('span', 'restlbl', 'Recover'));
        } else {
          li.appendChild(el('span', 'restlbl', key === PLAN.raceDate ? '' : 'Rest'));
        }
        li.appendChild(dayChips(key, d, t));
        list.appendChild(li);
      }
      sec.appendChild(el('h3', 'wh', 'Week ' + weekNo + ' <small>' + done7 + '/' + tot7 + '</small>'));
      sec.appendChild(list);
      wrap.appendChild(sec);
    }
    summary();
  }

  // Yes/no checks for strength training and sauna, on any day (not just run days).
  var CHIPS = [['strength', '\ud83c\udfcb\ufe0f', 'Strength training'], ['sauna', '\ud83e\uddd6', 'Sauna']];
  var BIKE_NEXT = { '': 'indoor', indoor: 'outdoor', outdoor: '' };   // tap to cycle: off, indoor, outdoor, off
  function dayChips(key, d, t) {
    var box = el('div', 'chips'), cur = store.days[key] || {};
    CHIPS.forEach(function (c) {
      var b = el('button', 'chip'); b.type = 'button';
      var on = !!cur[c[0]];
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('aria-label', c[2] + ', ' + fmt(d));
      b.title = c[2];
      b.disabled = !store.canEdit;
      b.innerHTML = '<span aria-hidden="true">' + c[1] + '</span><span class="chiplbl">' + (c[0] === 'strength' ? 'Strength' : 'Sauna') + '</span>';
      b.addEventListener('click', function () {
        var patch = {}; patch[c[0]] = !on;
        store.setDay(key, patch).then(function () { banner(''); render(); })
          .catch(function () { banner('Could not save. Check your connection and try again.'); });
      });
      box.appendChild(b);
    });
    // Bike: one chip that cycles off -> indoor -> outdoor -> off
    var bike = cur.bike || '', bb = el('button', 'chip'); bb.type = 'button';
    bb.setAttribute('aria-pressed', bike ? 'true' : 'false');
    bb.setAttribute('aria-label', 'Bike ride, ' + fmt(d) + ': ' + (bike || 'none') + '. Press to change.');
    bb.title = 'Bike ride: tap to cycle indoor, outdoor, off';
    bb.disabled = !store.canEdit;
    bb.innerHTML = '<span aria-hidden="true">\ud83d\udeb4</span><span class="chiplbl">' + (bike ? 'Bike \u00b7 ' + (bike === 'indoor' ? 'in' : 'out') : 'Bike') + '</span>';
    bb.addEventListener('click', function () {
      store.setDay(key, { bike: BIKE_NEXT[bike] || null }).then(function () { banner(''); render(); })
        .catch(function () { banner('Could not save. Check your connection and try again.'); });
    });
    box.appendChild(bb);
    return box;
  }

  function defaultDate(s) { var t = iso(today()); return s.date <= t ? s.date : t; }
  function hasDetails(e) { return e && (e.distance_mi != null || e.duration_min != null || e.run_pct != null || e.note); }

  function quickToggle(s) {
    if (!store.canEdit) return;
    var p;
    if (done(s.id)) {
      if (hasDetails(store.entries[s.id]) && !confirm('Remove the log for "' + s.title + '"? Its distance, time and notes will be deleted.')) return;
      p = store.remove(s.id);
    } else {
      p = store.save(s.id, { date: defaultDate(s), distance_mi: null, duration_min: null, run_pct: null, note: null });
    }
    p.then(function () { banner(''); render(); if (dlg.open && current && current.id === s.id) fillDetail(current); })
     .catch(function () { banner('Could not save. Check your connection and try again.'); });
  }

  // ---- detail dialog + log form ---------------------------------------
  var dlg = document.getElementById('detail'), body = document.getElementById('detailBody');

  function openDetail(s) {
    current = s;
    fillDetail(s);
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
  }
  dlg.addEventListener('close', function () { stopTimer(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });

  function fillDetail(s) {
    stopTimer();
    body.innerHTML = '';
    body.appendChild(el('p', 'eyebrow', fmt(parse(s.date)) + (s.race ? ' &middot; Race day' : ' &middot; Week ' + s.week)));
    var h = el('h2', null, esc(s.title)); h.id = 'dTitle'; body.appendChild(h);
    body.appendChild(el('p', 'meta', minLabel(total(s)) + ' total &middot; ' + minLabel(runTotal(s)) + ' of running'));
    body.appendChild(bar(s));
    var ol = el('ol', 'steps');
    s.segs.forEach(function (g) { ol.appendChild(el('li', g.type, '<b>' + (g.type === 'run' ? 'Run' : 'Walk') + '</b> ' + mmss(g.sec))); });
    body.appendChild(ol);
    body.appendChild(el('p', 'tip', esc(s.tip)));

    if (!s.race && store.canEdit) {
      var act = el('div', 'actions');
      var start = el('button', 'btn primary', 'Start guided workout'); start.type = 'button';
      start.addEventListener('click', function () { startTimer(s); });
      act.appendChild(start);
      body.appendChild(act);
      body.appendChild(el('div', 'timerbox'));
    }
    body.appendChild(logSection(s));
  }

  function logSection(s) {
    var e = store.entries[s.id], sec = el('section', 'logbox');
    sec.appendChild(el('h3', null, 'What you actually did'));
    if (!store.canEdit) {
      sec.appendChild(el('p', 'meta', e ? esc((fmt(parse(e.date))) + (logLine(e) ? ' · ' + logLine(e) : '')) : 'Nothing logged yet.'));
      if (e && e.note) sec.appendChild(el('p', 'tip', esc(e.note)));
      return sec;
    }
    var f = el('form', 'logform');
    var plannedRunPct = Math.round(100 * runTotal(s) / total(s));
    f.innerHTML =
      '<div class="import"><button type="button" class="btn small" id="importBtn">Import from Garmin (.tcx or .gpx)</button>' +
        '<input type="file" id="importFile" accept=".tcx,.gpx,.xml,text/xml,application/xml,application/gpx+xml" hidden>' +
        '<p class="importmsg" role="status" id="importMsg">Export the activity from Garmin Connect on the web (gear icon, Export to TCX or GPX). The file is read on this device and not uploaded.</p></div>' +
      '<label>Date <input type="date" name="date" required></label>' +
      '<div class="row2">' +
        '<label>Distance (miles) <input type="number" name="distance" min="0" max="50" step="0.01" inputmode="decimal" placeholder="e.g. 2.1"></label>' +
        '<label>Time (minutes) <input type="number" name="duration" min="0" max="600" step="0.1" inputmode="decimal" placeholder="e.g. 32"></label>' +
      '</div>' +
      '<div class="pctbox"><label class="chk"><input type="checkbox" name="usepct"> Estimate how much was running vs. walking</label>' +
        '<div class="pctrow"><input type="range" name="pct" min="0" max="100" step="5" value="' + plannedRunPct + '" disabled>' +
        '<output name="pctout"></output></div>' +
        '<p class="hint">Percent of your total time spent running. The plan for this day is about ' + plannedRunPct + '%.</p></div>' +
      '<label>Notes <textarea name="note" rows="3" maxlength="1000" placeholder="How did it feel? Weather, route, aches, anything."></textarea></label>' +
      '<p class="formerr" role="alert" hidden></p>';
    var date = f.elements.date, dist = f.elements.distance, dur = f.elements.duration, use = f.elements.usepct,
        pct = f.elements.pct, out = f.elements.pctout, note = f.elements.note, err = f.querySelector('.formerr');
    date.value = e ? e.date : defaultDate(s);
    if (e) {
      if (e.distance_mi != null) dist.value = e.distance_mi;
      if (e.duration_min != null) dur.value = e.duration_min;
      if (e.run_pct != null) { use.checked = true; pct.disabled = false; pct.value = e.run_pct; }
      if (e.note) note.value = e.note;
    }
    function showPct() { out.textContent = use.checked ? pct.value + '% running · ' + (100 - pct.value) + '% walking' : 'Not set'; }
    use.addEventListener('change', function () { pct.disabled = !use.checked; showPct(); });

    var impBtn = f.querySelector('#importBtn'), impFile = f.querySelector('#importFile'), impMsg = f.querySelector('#importMsg');
    impBtn.addEventListener('click', function () { impFile.click(); });
    impFile.addEventListener('change', function () {
      var file = impFile.files && impFile.files[0];
      impFile.value = '';
      if (!file) return;
      function say(m, bad) { impMsg.textContent = m; impMsg.classList.toggle('bad', !!bad); }
      if (file.size > 8 * 1024 * 1024) return say('That file is too large. Export a single activity.', true);
      file.text().then(function (txt) {
        var r = C25K_IMPORT.parseText(txt, file.name);
        if (r.date) date.value = r.date;
        dist.value = r.distance_mi;
        dur.value = r.duration_min;
        var bits = [r.distance_mi + ' mi in ' + r.duration_min + ' min'];
        if (r.run_pct != null) {
          use.checked = true; pct.disabled = false; pct.value = r.run_pct; showPct();
          bits.push('running share estimated at ' + r.run_pct + '% from ' + (r.basis === 'cadence' ? 'cadence and speed' : 'speed'));
        } else {
          bits.push('not enough movement to estimate running share');
        }
        var warn = !r.sport || /run|walk|hik|other|trail|treadmill|track|street/i.test(r.sport) ? '' : ' This looks like a ' + r.sport + ' activity.';
        say('Imported ' + file.name + ': ' + bits.join('; ') + '. Check the numbers, then save.' + warn, false);
      }).catch(function (er) {
        say(er && er.friendly ? er.message : 'Could not read that file. Try exporting it as TCX or GPX.', true);
      });
    });
    pct.addEventListener('input', showPct);
    showPct();

    var acts = el('div', 'actions');
    var save = el('button', 'btn primary', e ? 'Update log' : 'Save and mark done'); save.type = 'submit';
    acts.appendChild(save);
    if (e) {
      var rm = el('button', 'btn', 'Remove log'); rm.type = 'button';
      rm.addEventListener('click', function () {
        if (hasDetails(e) && !confirm('Delete this log, including distance, time and notes?')) return;
        store.remove(s.id).then(function () { render(); fillDetail(s); }).catch(function () { showErr('Could not remove it. Try again.'); });
      });
      acts.appendChild(rm);
    }
    f.appendChild(acts);
    function showErr(m) { err.hidden = !m; err.textContent = m || ''; }
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      showErr('');
      var entry = {
        date: date.value,
        distance_mi: dist.value === '' ? null : Number(dist.value),
        duration_min: dur.value === '' ? null : Number(dur.value),
        run_pct: use.checked ? Number(pct.value) : null,
        note: note.value.trim() || null
      };
      save.disabled = true; save.textContent = 'Saving…';
      store.save(s.id, entry).then(function () { banner(''); render(); fillDetail(s); })
        .catch(function (er) { save.disabled = false; save.textContent = e ? 'Update log' : 'Save and mark done'; showErr(er && er.status === 400 ? er.message : 'Could not save. Check your connection and try again.'); });
    });
    sec.appendChild(f);
    return sec;
  }

  // ---- guided timer ---------------------------------------------------
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
        box.innerHTML = '<strong>Nice work.</strong> Log how it went below.';
        return;
      }
      left = s.segs[idx].sec; cue(s.segs[idx]); paint();
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

  // ---- start ----------------------------------------------------------
  document.getElementById('reset').addEventListener('click', function () {
    if (store.mode !== 'local') return;
    if (confirm('Clear everything you have logged on this device?')) { store.reset().then(reload); }
  });

  C25K.open().then(function (st) {
    store = st;
    if (store.error === 'unknown') {
      banner('That link is not recognized. Check that you copied the whole thing, or ask for a new one.');
      store.canEdit = false; store.level = 'beginner';
    } else if (store.error === 'network') {
      banner('Could not reach the server, so your saved log is not shown. Try again in a bit.');
      store.canEdit = false;
    }
    if (!store.error) who();
    reload();
    requestAnimationFrame(function () { document.getElementById('ring').classList.add('ready'); });
  });
})();
