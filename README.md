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
