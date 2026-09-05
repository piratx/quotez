# quote-signature

Renders a random quote (from `quotes/*.md`) as a transparent PNG
(`quote.png`), regenerated every 15 minutes by a GitHub Action.

## Use in an email signature

Add this once to your Mail signature, after your normal sign-off:

    <img src="https://raw.githubusercontent.com/USERNAME/REPO/main/quote.png" style="max-width:480px" alt="">

Replace USERNAME/REPO with this repo's actual path. That's it — never
touch the signature again. Mail (and your recipients' mail clients)
fetch this URL fresh each time they render the signature, so it shows
whatever quote.png currently contains.

## Adding more quotes

Drop another `.md` file into `quotes/` — same format as the existing
ones (a quote, then the attribution name on its own line, optionally
with YAML frontmatter and a `# heading` above it). No other setup
needed; the next scheduled run will start picking it up too.

## Manually trigger a rotation

Actions tab → "Rotate signature quote" → Run workflow. Or just wait —
it runs automatically every 15 minutes.
