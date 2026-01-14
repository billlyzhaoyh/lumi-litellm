# Welcome to Lumi-Litellm clone

This is a clone of the [Lumi](https://github.com/PAIR-code/lumi) project,
using [LiteLLM](https://github.com/BerriAI/litellm) as the main LLM engine
in the backend instead of the original
[Gemini API](https://ai.google.dev/gemini-api/terms). I am currently using
OpenAI's API for this.

Lumi uses AI to help you quickly read and
understand [arXiv papers](https://arxiv.org/). Features include:

- ✏️ **AI-augmented annotations** - read summaries at multiple granularities
- 🔖 **Smart highlights** - highlight text + ask questions
- 🖼️ **Figure explanations** - ask Lumi about images in the paper

![Screenshots of Lumi desktop and mobile views](assets/combined_desktop_mobile.png)

*Please note that Lumi can only currently process arXiv papers under a
Creative Commons license.*

## Running Lumi locally

### Start frontend web app

```bash
cd frontend  # If navigating from top level
npm install  # Only run once

# Create an index.html file
cp index.example.html index.html

npm run start
```

Then, view the app at <http://localhost:4201>.

### Storybook stories

To view [Storybook](https://storybook.js.org/docs) stories for Lumi:

```bash
npm run storybook
```

Then, view the stories at <http://localhost:6006>.

### Local paper import and debugging

The import script in `scripts/import_papers_local.py` can be used to import a
set of papers for local debugging.

The locally imported papers can be rendered in `lumi_doc.stories.ts`
via Storybook.
