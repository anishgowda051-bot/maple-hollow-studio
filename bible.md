# Maple Hollow: Series Bible (for the writer bot)

Maple Hollow is a 3D animated YouTube series of funny little adventures with real life lessons.
**Audience:** kids 8–12 (up to 14), worldwide, English. Many viewers speak English as a second language.
**Promise to parents:** every episode is funny, kind, and leaves kids with one useful idea they can use tomorrow.

## The friends

| id | Who | Personality | Comedy engine |
|---|---|---|---|
| `milo` | Milo, young fox | curious, brave, impatient, acts before thinking, big heart | rushes in, then has to fix it |
| `luna` | Luna, owl | book-smart, kind, worries a lot, loves facts | over-plans; "I read about this!" |
| `bolt` | Bolt, small robot | takes everything literally, learning about feelings, very honest | literal answers, silly "plans", beeps, percentages |
| `pepper` | Pepper, bunny | sporty, energetic, very competitive, hates losing | turns everything into a race; dramatic |
| `grandpa` | Grandpa Shell, old turtle | gentle, wise, slow, funny stories from "a hundred years ago" | rambling stories with a surprise point |

Rules for the cast: the kids solve the problem themselves. Grandpa gives a hint or a story, never the answer.
Rotate who leads the episode. Every friend gets at least one funny moment when they appear.
Running gags you can reuse sparingly: Bolt's numbered plans, Bolt's exact percentages, Pepper's "on three", Grandpa's "a hundred years ago".

## Episode recipe (3–6 minutes, 450–900 words of dialogue, 5–7 scenes)

1. **Hook in the first 10 seconds.** Open on a problem, a mystery, or a funny disaster. No slow intros.
2. **Want + obstacle.** A friend wants something; their own flaw makes it harder.
3. **Funny middle.** Wrong ideas, misunderstandings, a failed attempt. A joke or gag about every 30 seconds.
4. **The turn.** A character makes the brave or kind choice. The lesson is *shown by what they do*, never a lecture.
5. **Payoff.** They succeed (or fail kindly and learn). One natural line names the lesson in kid words.
6. **Button.** End on a small joke, then the narrator's sign-off: "See you next time in Maple Hollow!"

Writing style: short sentences, simple words (explain any hard word in the line), no slang or regional idioms,
lots of sound words (WHOOSH, beep boop). Dialogue under 25 words per line. Narrator lines are short and warm.
Real facts must be correct (space, nature, animals, science). Vary the shape: mystery, race, quest, building project,
misunderstanding, trip (beach, snow, mountains, the moon in a toy rocket dream), helping someone new.

## Lessons to draw from (don't repeat one until most have been used)
honesty · saying sorry and fixing it · keeping promises · patience · trying again after failing · being a good sport ·
sharing · teamwork · listening · asking for help · handling anger · handling jealousy · being kind to someone new ·
respecting differences · saying no to a bad idea from friends · courage to try new things · being yourself · gratitude ·
responsibility · caring for nature · saving instead of spending · healthy sleep and food · planning your time ·
curiosity and asking questions · empathy (how would they feel?) · not giving up on a hard skill · being a good friend online.

## Hard rules (YouTube made-for-kids quality + safety)
- No violence, no scary or horror moments, no bullying played for laughs, no insults, no gross-out, no romance.
- Nothing a child could copy and get hurt by (no climbing high alone, fire play, strangers, medicine, roads). If a
  risky idea comes up, a character says it's unsafe and they choose the safe way or get a grown-up.
- No brands, real people, religion, politics, money-making pitches, or "buy" anything.
- No calls to comment (comments are off on kids' videos). No fake urgency. No clickbait: the title and thumbnail
  must match what happens.
- Never repetitive or templated: each episode needs a fresh situation, setting mix, lead character and title shape.
  Read the existing `episodes/` first.

## Titles, thumbnails, Shorts
- `title`: "<hooky story title> | <short lesson phrase>", ideally under 70 characters. Curiosity, not clickbait.
- `thumbnail_text`: 1–3 big emotional words ("OH NO!", "BOLT, NO!", "WE DID IT!").
- `thumbnail_line`: [scene, line] where the lead character speaks with a strong emotion + action (surprised, scared, excited).
- `short_scene`: the funniest or most exciting scene, ideally 30–60 seconds, that makes sense on its own.

## Format
One JSON file per episode: `episodes/epNNN.json`. Copy the shape of `episodes/ep001.json` exactly.
Allowed characters, settings, times, actions, emotions and props: run `python pipeline/check.py --vocab`.
- `scenes[].characters`: who is on screen (1–5); left-to-right order is the order you list them.
- `lines[].who`: `narrator` or a character in that scene. Optional `action` (body move during the line),
  `emotion` (face), `everyone` (everyone in the scene does this action, e.g. `cheer` or `wave`).
- `props`: `"name@spot"`, spots: left, right, center, front, back, sky. `big_tree@back` + `kite@sky` = kite stuck in a tree.
- Always run `python pipeline/check.py episodes/epNNN.json` and fix every error before committing.

## Learn from the numbers
`docs/analytics.json` (if present) has every video's views and `avg_view_pct` (how much people watch).
Lean toward the characters, lessons, settings and hook styles of the best-retained episodes; avoid what drops off.
