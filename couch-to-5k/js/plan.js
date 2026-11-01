// Plan data for the Couch to Turkey Trot page. Durations are in seconds.
// Dates are local calendar dates (YYYY-MM-DD). Race: Thanksgiving, Thu Nov 26, 2026.
(function () {
  var RACE_DATE = '2026-11-26';
  var WARM = 300, COOL = 300;

  function seg(type, sec) { return { type: type, sec: sec }; }
  // reps x (run, walk), dropping the final walk (the cooldown covers it)
  function rr(reps, run, walk) {
    var out = [];
    for (var i = 0; i < reps; i++) {
      out.push(seg('run', run));
      if (i < reps - 1) out.push(seg('walk', walk));
    }
    return out;
  }
  function build(main) {
    return [seg('walk', WARM)].concat(main, [seg('walk', COOL)]);
  }
  var m = 60;

  var sessions = [
    { id: 's01', date: '2026-11-02', title: 'First steps', week: 1,
      segs: build(rr(8, 1 * m, 2 * m)),
      tip: 'Run slowly enough to talk. Walking is part of the plan, not a failure.' },
    { id: 's02', date: '2026-11-04', title: 'Finding a rhythm', week: 1,
      segs: build(rr(8, 90, 90)),
      tip: 'Relax your shoulders and keep your steps short and quick.' },
    { id: 's03', date: '2026-11-06', title: 'Two-minute runs', week: 1,
      segs: build(rr(6, 2 * m, 90)),
      tip: 'Breathe in a steady rhythm. If you gasp, slow down; do not stop.' },
    { id: 's04', date: '2026-11-09', title: 'Three-minute runs', week: 2,
      segs: build(rr(5, 3 * m, 2 * m)),
      tip: 'Five runs of three minutes: more running than walking from here on.' },
    { id: 's05', date: '2026-11-11', title: 'Four-minute runs', week: 2,
      segs: build(rr(4, 4 * m, 2 * m)),
      tip: 'Same easy pace as before. Do not speed up because it feels okay.' },
    { id: 's06', date: '2026-11-13', title: 'Five-minute runs', week: 2,
      segs: build(rr(3, 5 * m, 2 * m)),
      tip: 'Halfway through the plan. You are running 15 minutes in total.' },
    { id: 's07', date: '2026-11-16', title: 'Eight minutes', week: 3,
      segs: build([seg('run', 8 * m), seg('walk', 2 * m), seg('run', 8 * m), seg('walk', 2 * m), seg('run', 6 * m)]),
      tip: 'The big jump. If 8 minutes is too much, run 6 and walk 1 instead.' },
    { id: 's08', date: '2026-11-18', title: 'Ten and ten', week: 3,
      segs: build([seg('run', 10 * m), seg('walk', 2 * m), seg('run', 10 * m)]),
      tip: 'Two 10-minute runs: 20 minutes of running, with a walk in the middle.' },
    { id: 's09', date: '2026-11-20', title: 'Fifteen and ten', week: 3,
      segs: build([seg('run', 15 * m), seg('walk', 2 * m), seg('run', 10 * m)]),
      tip: 'Your longest run so far. Go slower than you think you need to.' },
    { id: 's10', date: '2026-11-23', title: 'Dress rehearsal', week: 4,
      segs: build(rr(3, 10 * m, 1 * m)),
      tip: 'About the length of the race. Wear what you will wear on Thursday, and test your breakfast.' },
    { id: 's11', date: '2026-11-25', title: 'Shakeout', week: 4,
      segs: build(rr(3, 2 * m, 1 * m)),
      tip: 'Short and easy. Then lay out your clothes and check the start time and parking.' },
    { id: 'race', date: '2026-11-26', title: 'Turkey Trot', week: 4, race: true,
      segs: rr(4, 9 * m, 1 * m),
      tip: 'Walk 5 minutes to warm up first. Then start slower than feels necessary: run 9, walk 1, and enjoy it. Walking is allowed.' }
  ];

  window.PLAN = { raceDate: RACE_DATE, sessions: sessions, firstMonday: '2026-11-02', lastDay: '2026-11-29' };
})();
