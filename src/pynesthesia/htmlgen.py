import json
from pathlib import Path

ADJECTIVES = ["bright", "bold", "fresh", "hopeful", "promising", "quiet", "powerful", "unexpected"]
IDEA_VERBS = ["grow", "emerge", "evolve", "deepen", "spread", "resonate", "bloom", "take root"]
OPPORTUNITY_VERBS = ["appear", "arrive", "emerge", "unfold", "arise", "return", "surface", "knock"]

BKG_COLORS = [
    "#f4d6d6",  # light red
    "#f8dcc5",  # light orange
    "#f8efd0",  # cream
    "#f1f5d2",  # yellow green
    "#e6f8dc",  # light green
    "#ddf9f3",  # mint
    "#c8def4",  # light blue
    "#dac9f3"   # light purple
]

FONT_COLORS = [
    "#2C394B",  # gray blue
    "#1C3258",  # navy blue
    "#363450",  # dark blue-purple?
    "#2C3D31",  # dark green
    "#422720",  # dark red
    "#2c2c2c",  # gray
    "#3d324d",  # dark purple
    "#253c36"   # dark turquoise?
]

FONTS = [
    "Georgia, serif",
    "Arial, sans-serif",
    "Verdana, sans-serif",
    "'Trebuchet MS', sans-serif",
    "'Palatino Linotype', serif",
    "'Courier New', monospace",
    "Tahoma, sans-serif",
    "Garamond, serif",
]

CORNER_DECORATIONS = ["✦", "✿", "❋", "✧", "☼", "❀", "❉", "✺"]

def generate_cards(seed_hash):
    seed = bytes.fromhex(seed_hash)
    if len(seed) != 32:
        raise ValueError("expected a sha-256 hash")

    cards = []

    for element_number in range(3):
        start = element_number * 10

        first_adj = ADJECTIVES[seed[start] % 8]
        second_adj = ADJECTIVES[seed[start + 1] % 8]
        idea_verb = IDEA_VERBS[seed[start + 2] % 8]
        opp_verb = OPPORTUNITY_VERBS[seed[start + 3] % 8]

        if element_number == 0:
            header = "Yesterday's Fortune"
            body = (f"Yesterday, a {first_adj} idea helped you {idea_verb}. Remember that feeling when it {opp_verb}s again.")
        if element_number == 1:
            header = "Today's Fortune"
            body = (f"Something {first_adj} may {opp_verb} without warning. Be prepared to let that {second_adj} thing {idea_verb}.")
        if element_number == 2:
            header = "Tomorrow's Fortune"
            body = (f"Tomorrow, be {first_adj} if a complicated situation {opp_verb}s. Something {second_adj} may {idea_verb} if you take a risk.")

        page_color = seed[start + 4] % 8
        card_color = seed[start + 5] % 8

        if card_color == page_color:
            card_color = (card_color + 1) % 8

        heading_color = seed[start + 6] % 8
        body_color = seed[start + 7] % 8

        if body_color == heading_color:
            body_color = (body_color + 1) % 8

        cards.append({
            "header": header,
            "body": body,
            "page_color": BKG_COLORS[page_color],
            "card_color": BKG_COLORS[card_color],
            "heading_color": FONT_COLORS[heading_color],
            "body_color": FONT_COLORS[body_color],
            "font": FONTS[seed[start + 8] % 8],
            "corner_decoration": CORNER_DECORATIONS[seed[start + 9] % 8],
            "border_color": FONT_COLORS[heading_color]
        })

    return cards

HTML = """<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Three Fortunes</title>
	<style>
		* { box-sizing: border-box; }

		body {
			margin: 0;
			min-height: 100vh;
			padding: 24px;
			display: grid;
			place-items: center;
		}

		main {
			width: 100%;
			max-width: 650px;
			min-height: 430px;
			padding: 48px;
			border: 1px solid;
			border-radius: 24px;
			box-shadow: 0 10px 30px #0002;
			position: relative;
			overflow: hidden;
		}

		main::before {
			content: "";
			position: absolute;
			width: 200px;
			height: 200px;
			right: -80px;
			top: -80px;
			border-radius: 50%;
			opacity: .4;
		}

		.top, h1, p, .rule, nav, .deco {
			position: relative;
		}

		.top {
			font: bold 16px;
			letter-spacing: 2px;
			text-transform: uppercase;
		}

		h1 {
			max-width: 450px;
			margin: 24px 0 16px;
			font-size: 48px;
			line-height: 1;
			font-weight: normal;
		}

		p {
			max-width: 470px;
			font-size: 20px;
			line-height: 1.6;
		}

		.rule {
			width: 60px;
			height: 3px;
			margin: 28px 0;
			border-radius: 4px;
		}

		.deco {
			position: absolute;
			right: 32px;
			top: 26px;
			font-size: 50px;
		}

		nav {
			display: flex;
			justify-content: space-between;
			margin-top: 32px;
		}

		button {
			padding: 10px 10px;
			border: 1px solid;
			border-radius: 20px;
			background: transparent;
			font: 14px;
            font-family: inherit;
			cursor: pointer;
		}

		button:disabled {
			opacity: .4;
			cursor: default;
		}
	</style>
</head>
<body>
    <main id="card">
        <div class="top" id="header"></div>
        <div class="rule"></div>
        <h1 id="fortune"></h1>
        <span class="deco" id="deco" aria-hidden="true"></span>
        <nav>
            <button id="back" onclick="show(-1)">&lt;</button>
            <button id="next" onclick="show(1)">&gt;</button>
        </nav>
    </main>

	<script>
		const cards = __CARDS__;
		let current = 0;

		function show(step = 0) {
			current += step;
			const c = cards[current];
			document.body.style.background = c.page_color;

			const card = document.querySelector("#card");
			card.style.background = c.card_color;
			card.style.borderColor = c.border_color;
			card.style.fontFamily = c.font;

			document.querySelector("#header").textContent = c.header;
			document.querySelector("#header").style.color = c.body_color;
			document.querySelector("#fortune").textContent = c.body;
			document.querySelector("#fortune").style.color = c.heading_color;
			document.querySelector(".rule").style.background = c.border_color;
			document.querySelector("#deco").textContent = c.corner_decoration;
			document.querySelector("#deco").style.color = c.border_color;
			document.querySelector("#back").disabled = current === 0;
			document.querySelector("#next").disabled = current === cards.length - 1;
		}

		show();
	</script>
</body>
</html>
"""

def write_html(cards, filename="fortunes.html"):
	html = HTML.replace("__CARDS__", json.dumps(cards))
	Path(filename).write_text(html, encoding="utf-8")