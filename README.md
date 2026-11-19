# Website of Mobile Brain Games

https://mobilebraingames.com

This is a Jekyll site deployed through GitHub Pages. Product pages live in
`_posts`, articles in `_blog`, and the games directory reads the
`directory_group` field from each product's front matter.

## Local checks

Install the dependencies with `bundle install`, then run `bundle exec rake test`.
That builds the site, checks rendered metadata, JSON-LD, sitemap URLs and
internal links, and runs HTML-Proofer. The same core build and rendered-site
check runs on pull requests.

## Release Flame

Run `python3 scripts/import_flame.py /absolute/path/to/flame-web.zip` to import
new game assets. The importer preserves the site's `flame/index.html` wrapper
and `/js/flame-player.js` gate: phones see the Android download message without
loading Flutter; desktops and tablets can play. Run `node --test tests/flame-player.test.cjs`
and `bundle exec rake test` before publishing to `main`.
