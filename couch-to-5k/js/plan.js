// Plan data for the Couch to Turkey Trot page. Durations are in seconds.
// Dates are local calendar dates (YYYY-MM-DD). Race: Thanksgiving, Thu Nov 26, 2026.
// Three tracks share the same dates and session ids; they differ in how much running each session asks for.
(function () {
  var RACE_DATE = '2026-11-26';
  var WARM = 300, COOL = 300, m = 60;

  function seg(type, sec) { return { type: type, sec: sec }; }
  function run(min) { return seg('run', min * m); }
  function walk(min) { return seg('walk', min * m); }
  // reps x (run, walk), dropping the final walk (the cooldown covers it)
  function rr(reps, runSec, walkSec) {
    var out = [];
    for (var i = 0; i < reps; i++) {
      out.push(seg('run', runSec));
      if (i < reps - 1) out.push(seg('walk', walkSec));
    }
    return out;
  }
  function build(main) { return [seg('walk', WARM)].concat(main, [seg('walk', COOL)]); }

  // id, date, week are shared. Each track supplies title, segments and a tip per session.
  var base = [
    { id: 's01', date: '2026-11-02', week: 1 }, { id: 's02', date: '2026-11-04', week: 1 },
    { id: 's03', date: '2026-11-06', week: 1 }, { id: 's04', date: '2026-11-09', week: 2 },
    { id: 's05', date: '2026-11-11', week: 2 }, { id: 's06', date: '2026-11-13', week: 2 },
    { id: 's07', date: '2026-11-16', week: 3 }, { id: 's08', date: '2026-11-18', week: 3 },
    { id: 's09', date: '2026-11-20', week: 3 }, { id: 's10', date: '2026-11-23', week: 4 },
    { id: 's11', date: '2026-11-25', week: 4 }, { id: 'race', date: '2026-11-26', week: 4, race: true }
  ];

  var tracks = {
    beginner: {
      label: 'Starting from the couch',
      blurb: 'Little or no regular running. Short run/walk intervals that build up.',
      s: {
        s01: ['First steps', build(rr(8, 1 * m, 2 * m)), 'Run slowly enough to talk. Walking is part of the plan, not a failure.'],
        s02: ['Finding a rhythm', build(rr(8, 90, 90)), 'Relax your shoulders and keep your steps short and quick.'],
        s03: ['Two-minute runs', build(rr(6, 2 * m, 90)), 'Breathe in a steady rhythm. If you gasp, slow down; do not stop.'],
        s04: ['Three-minute runs', build(rr(5, 3 * m, 2 * m)), 'Five runs of three minutes: more running than walking from here on.'],
        s05: ['Four-minute runs', build(rr(4, 4 * m, 2 * m)), 'Same easy pace as before. Do not speed up because it feels okay.'],
        s06: ['Five-minute runs', build(rr(3, 5 * m, 2 * m)), 'Halfway through the plan. You are running 15 minutes in total.'],
        s07: ['Eight minutes', build([run(8), walk(2), run(8), walk(2), run(6)]), 'The big jump. If 8 minutes is too much, run 6 and walk 1 instead.'],
        s08: ['Ten and ten', build([run(10), walk(2), run(10)]), 'Two 10-minute runs: 20 minutes of running, with a walk in the middle.'],
        s09: ['Fifteen and ten', build([run(15), walk(2), run(10)]), 'Your longest run so far. Go slower than you think you need to.'],
        s10: ['Dress rehearsal', build(rr(3, 10 * m, 1 * m)), 'About the length of the race. Wear what you will wear on Thursday, and test your breakfast.'],
        s11: ['Shakeout', build(rr(3, 2 * m, 1 * m)), 'Short and easy. Then lay out your clothes and check the start time and parking.'],
        race: ['Turkey Trot', rr(4, 9 * m, 1 * m), 'Walk 5 minutes to warm up first. Then start slower than feels necessary: run 9, walk 1, and enjoy it. Walking is allowed.']
      }
    },
    intermediate: {
      label: 'Can already run about 5 minutes',
      blurb: 'Comfortable with a few minutes of jogging. Longer runs from the start, fewer walk breaks.',
      s: {
        s01: ['Warm-up intervals', build(rr(5, 3 * m, 1 * m)), 'Easy pace. These are short on purpose; the first week is for settling in.'],
        s02: ['Five-minute runs', build(rr(4, 5 * m, 1 * m)), 'Conversational pace. Take the walk breaks even when you feel good.'],
        s03: ['Eight-minute runs', build(rr(3, 8 * m, 1 * m)), 'Three solid runs. Keep your shoulders loose.'],
        s04: ['Twelve and twelve', build([run(12), walk(2), run(12)]), 'Two long runs with a walk between. Hold the same easy effort in both.'],
        s05: ['Fifteen and ten', build([run(15), walk(2), run(10)]), 'Start the first run slower than you want to.'],
        s06: ['Eighteen minutes', build([run(18)]), 'First long continuous run. Slow is fine.'],
        s07: ['Three tens', build(rr(3, 10 * m, 1 * m)), 'Same total as a race-length run, with short breaks.'],
        s08: ['Long and steady', build([run(22)]), 'A steady 22 minutes. If it hurts, walk a minute and carry on.'],
        s09: ['Two fifteens', build([run(15), walk(1), run(15)]), 'Your longest day. Keep the pace even.'],
        s10: ['Dress rehearsal', build([run(30)]), 'About race length. Wear Thursday\'s clothes and test your breakfast.'],
        s11: ['Shakeout', build(rr(3, 5 * m, 1 * m)), 'Short and easy. Then lay out your clothes and check the start time and parking.'],
        race: ['Turkey Trot', [run(20), walk(1), run(20)], 'Walk 5 minutes to warm up first. Start slower than feels necessary, and walk through water stops if you want to.']
      }
    },
    runner: {
      label: 'Already running 20+ minutes',
      blurb: 'Regular runner. Mostly easy continuous runs; the aim is a comfortable race.',
      s: {
        s01: ['Easy 20', build([run(20)]), 'Easy and conversational. Save the speed for race day.'],
        s02: ['Easy 25', build([run(25)]), 'Steady. Finish feeling like you could do more.'],
        s03: ['Easy 20', build([run(20)]), 'Keep it relaxed; this one is for recovery.'],
        s04: ['Steady 30', build([run(30)]), 'About the length of a 5K for most runners. Even pace.'],
        s05: ['Easy 25', build([run(25)]), 'Easy day after the 30.'],
        s06: ['Steady 30', build([run(30)]), 'Even effort the whole way.'],
        s07: ['Long 35', build([run(35)]), 'Your longest run of the plan. Very easy pace.'],
        s08: ['Easy 30', build([run(30)]), 'Comfortable and smooth.'],
        s09: ['Long 35', build([run(35)]), 'Last long run. Practice fueling and clothing.'],
        s10: ['Dress rehearsal', build([run(30)]), 'Run the last 10 minutes at your goal race pace; wear Thursday\'s clothes.'],
        s11: ['Shakeout', build([run(15)]), 'Short and easy. Lay out your clothes and check the start time and parking.'],
        race: ['Turkey Trot', [run(30)], 'Walk 5-10 minutes to warm up first. Start controlled, then pick it up in the last mile if you feel good.']
      }
    }
  };

  function sessionsFor(level) {
    var t = tracks[level] || tracks.beginner;
    return base.map(function (b) {
      var d = t.s[b.id];
      return { id: b.id, date: b.date, week: b.week, race: !!b.race, title: d[0], segs: d[1], tip: d[2] };
    });
  }

  window.PLAN = {
    raceDate: RACE_DATE, firstMonday: '2026-11-02', lastDay: '2026-11-29',
    levels: ['beginner', 'intermediate', 'runner'], tracks: tracks, sessionsFor: sessionsFor
  };
})();
