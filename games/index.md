---
layout: page
title: "Puzzle & Memory Games for Android, iOS and Web | Mobile Brain Games"
description: "Browse memory, pattern, word, maths, and reaction games. Compare supported platforms and find a game to download or play in your browser."
permalink: /games/
---

Choose a game by the kind of challenge you enjoy. Open any game to see how it plays, compare its supported platforms, and choose a download or browser-play option. Parents can use the [family guide]({{ '/parents/' | relative_url }}) to compare selected games.

## Play in your browser

- [Play Memory Match online]({{ '/memory-match/' | relative_url }}) — Find matching picture pairs on a phone, tablet, or computer without installing an app.
- [Play Flame on desktop]({{ '/flame/' | relative_url }}) — A separate keyboard-and-mouse flight challenge connected to Brain Game - Reaction & Speed. Desktop or laptop play only.

{% for group in site.data.game_groups %}
## {{ group.title }}

{{ group.description }}

{% assign group_posts = site.posts | where: 'directory_group', group.id | sort: 'home_order' %}
{% for game in group_posts %}
- <a href="{{ game.url | relative_url }}" data-app-select="{{ game.slug }}" data-app-select-placement="games-directory">{{ game.app_name }}</a> — {{ game.card_description }} {% if game.platforms %}{% for platform in game.platforms %}{% if platform.id == 'android' %}Android{% elsif platform.id == 'ios' %}iOS{% elsif platform.desktop_only %}Desktop web{% else %}Web{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}{% elsif game.ios_download %}Android, iOS{% if game.web_play_url %}, Web{% endif %}{% elsif game.web_play_url %}Android, {% if game.web_play_desktop_only %}Desktop web{% else %}Web{% endif %}{% else %}Android{% endif %}.
{% endfor %}
{% endfor %}
