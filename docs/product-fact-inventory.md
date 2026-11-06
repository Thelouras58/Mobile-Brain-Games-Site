# Product fact inventory

Browser verification on 2026-11-06 used the locally rendered release artifact in a real browser. Memory Match and Flame both reached their first rendered Flutter frame; Flame controls and eligibility guidance remained visible in the surrounding website content. This verifies the release artifact, not the not-yet-deployed production response.

Last reviewed: 2026-11-06

This inventory records facts used by the website during the SEO update. `public_listing` means the linked store page was reviewed; it does not mean the app was installed or tested on a device. Browser facts come from the repository's current public page and controls. Recheck listings before future substantive updates.

| Website product | Platform / public name | Facts used on website | Source | Method | Reviewed |
| --- | --- | --- | --- | --- | --- |
| Pattern Lock: Brain Games | Android / Pattern Lock: Brain Games! | Two core games in description; Hack The Pattern named in release notes; three number-game difficulties; offline; contains ads | [Google Play](https://play.google.com/store/apps/details?id=thelouras.pattern.game) | public_listing | 2026-11-06 |
| Simple Memory Game | Android / Memory Match: Brain Games | Matching, Sequence Recall, Play Together; daily challenges/history/statistics; offline; header says ads and IAP | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.simplememorygame.simple_memory_game) | public_listing | 2026-11-06 |
| Simple Memory Game | iOS / Simple Memory Training Game | Matching; four difficulties; calendar/history/themes; offline; no ads; no IAP | [App Store](https://apps.apple.com/us/app/simple-memory-training-game/id6786673240) | public_listing | 2026-11-06 |
| Simple Memory Game | Web / Memory Match | Browser card matching reached its first rendered frame; surrounding rules and Android/iOS options remained available | Local rendered `/memory-match/` release artifact | direct_testing | 2026-11-06 |
| Quick Tap | Android / Brain Game: Focus & Reaction! | Find numbers 1–25 in order; offline | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.number_focus) | public_listing | 2026-11-06 |
| Word Sprint | Android / Fast Word Puzzle Game | Timed dynamic letter grid; connect letters; unique words; longer words score higher; offline | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.wordsprint.word_sprint) | public_listing | 2026-11-06 |
| Processing Speed Training | Android / Brain Game - Reaction & Speed | Public listing positions the app as a reaction and processing-speed game | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.flame) | public_listing | 2026-11-06 |
| Processing Speed Training | Web / Flame | Separate desktop browser challenge reached its first rendered frame; controls remained visible outside the game surface | Local rendered `/flame/` release artifact | direct_testing | 2026-11-06 |
| Mobile Brain Games Premium | Android / Mobile Brain Games: Premium | Three-game daily sequence; five named free games and five named Premium games; optional Premium features; contains ads and offers IAP | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.mobile_brain_games_premium) | public_listing | 2026-11-06 |
| Quick Maths | Android / Quick Maths: Kids Brain Game | Ten timed questions per round; ten seconds per question; three difficulty levels; no ads | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.quickmaths) | public_listing | 2026-11-06 |
| Brain Trivia | Android / Neuroscience Quiz - Trivia | Brain-themed questions; Easy, Medium, and Hard settings; ad-free | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.brain_trivia) | public_listing | 2026-11-06 |
| CalmQuest | Android / CalmQuest: Anti-stress Games | Guided breathing, puzzle, pixel colouring, and virtual clicker activities | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.antistress.anti_stress_game) | public_listing | 2026-11-06 |
| Rate Your Mood | Android / Rate your Mood daily! | One-to-five emoji check-in; mood history; statistics; light/dark themes; reset option | [Google Play](https://play.google.com/store/apps/details?id=mobile.brain.games.rateyourmood.rate_your_mood) | public_listing | 2026-11-06 |

## Known ambiguity

The Memory Match Android listing header says “Contains ads · In-app purchases,” while its description says “No In-App Purchases.” The website therefore reports the store header label and explicitly notes the listing inconsistency instead of deciding which statement is correct. Direct device or Play Console verification is needed to resolve it.

## Claims removed or withheld

- The homepage's 80K+ collection-download claim was removed because no dated supporting source was available in the repository or public listing audit.
- Pattern Lock's previous “intended for ages 13 and over” statement was removed. The inspected Google Play listing instead showed a 3+ content rating; a content rating is not a publisher-defined audience.
- Mobile Brain Games Premium's previous “intended for ages 13 and over” statement was removed. The inspected listing was rated for everyone and did not support the website's earlier audience restriction.
- No direct device testing, airplane-mode testing, install conversion, or retention result is claimed.
- The Android and browser experiences associated with Processing Speed Training are described separately because public evidence does not establish feature parity.

## Screenshot gaps

- Pattern Lock currently has a difficulty-selection screenshot, not a screenshot demonstrating pattern recall or number drawing.
- Quick Tap and Word Sprint do not have product-page gameplay screenshots in the repository.
- New authentic gameplay captures require source/device access outside this content-only task. Do not replace them with fabricated screenshots.
