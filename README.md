# mtg-gpt-2-cloud-run

Code and UI for running a Magic card generator API using gpt-2-cloud-run. You can play with the API here.

It turns out GPT-2 overfits Magic card *very* quickly due to its more-structured format. The workaround is to use the random field encoding option offered by mtgencoding (which generates a random order for each individual card), generate such encodings many times, and concatenate them together. (e.g. via `concat.py`). As a bonus, this gives the network the ability to condition on any combination of fields. (see `encoding_examples.txt` for examples)

The network was trained with GPT-2 117M for 6500 steps (about 2 hours on a P100 / $1 with ). Despite that, there is still overfitting on names!

## Helpful Notes

* The network can recite existing card names and rules text, but rarely to the same card. The network often makes interesting color shift decisions with changes to CMC/Rarity.

## Maintainer/Creator

Max Woolf ([@minimaxir](https://minimaxir.com))

*Max's open-source projects are supported by his [Patreon](https://www.patreon.com/minimaxir). If you found this project helpful, any monetary contributions to the Patreon are appreciated and will be put to good creative use.*

## License

MIT

## Disclaimer

This repo has no affiliation or relationship with OpenAI or Wizards of the Coast.