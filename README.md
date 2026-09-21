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

## Updating app facts

Check the current Google Play listing linked by each product's `download`
field. Keep `store_name`, `offer_price`, and any ads, purchase, or offline
details consistent with that listing. Change `verified_on` and
`last_modified_at` only after reviewing the facts and updating the page.
Avoid adding ratings or health outcomes without a suitable first-party source.
