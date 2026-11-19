const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('js/flame-player.js', 'utf8');
const cases = [
  ['iPhone portrait', 'iPhone Mobile', 390, 844, 5, true],
  ['iPhone landscape', 'iPhone Mobile', 844, 390, 5, true],
  ['Android phone', 'Android Mobile', 412, 915, 5, true],
  ['Android landscape', 'Android Mobile', 915, 412, 5, true],
  ['phone desktop mode', 'X11 Linux x86_64', 915, 412, 5, true],
  ['iPad', 'iPad Mobile', 768, 1024, 5, false],
  ['iPad desktop mode', 'Macintosh', 820, 1180, 5, false],
  ['Android tablet', 'Android', 800, 1280, 5, false],
  ['small Android tablet', 'Android', 600, 960, 5, false],
  ['desktop', 'Windows NT', 1920, 1080, 0, false],
  ['small desktop screen', 'Macintosh', 500, 800, 0, false],
  ['touch laptop', 'Windows NT', 1366, 768, 10, false],
];
for (const [name, userAgent, width, height, maxTouchPoints, blocked] of cases) {
  test(name, () => {
    const elements = {'game-shell': {}, 'game-guide': {}, 'mobile-message': {hidden: true}, loading: {}};
    const scripts = [];
    let timers = 0;
    vm.runInNewContext(source, {
      navigator: {userAgent, maxTouchPoints}, screen: {width, height},
      document: {getElementById: id => elements[id], createElement: tag => ({tag}), body: {append: el => scripts.push(el)}},
      window: {addEventListener() {}}, setTimeout: () => ++timers,
    });
    assert.equal(elements['mobile-message'].hidden, !blocked);
    assert.equal(scripts.length, blocked ? 0 : 1);
    assert.equal(timers, blocked ? 0 : 1);
    if (blocked) {
      assert.equal(elements['game-shell'].hidden, true);
      assert.equal(elements['game-guide'].hidden, true);
    } else {
      assert.equal(scripts[0].src, 'flutter_bootstrap.js');
    }
  });
}
