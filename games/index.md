---
layout: page
title: "Android Games and Apps from Mobile Brain Games"
description: "Browse Mobile Brain Games by game type, from card matching and timed maths to words, reactions, and calmer play."
permalink: /games/
---

Choose a game by the kind of challenge you enjoy. Each page explains how its app works and links to the current Google Play listing. Availability may vary by region and device. Parents can use the [family guide]({{ '/parents/' | relative_url }}) to compare selected titles.

{% for group in site.data.game_groups %}
## {{ group.title }}

{{ group.description }}

{% assign group_posts = site.posts | where: 'directory_group', group.id | sort: 'home_order' %}
{% for game in group_posts %}
- [{{ game.app_name }}]({{ game.url | relative_url }}) — {{ game.card_description }}
{% endfor %}
{% endfor %}
