# Ulauncher ChatGPT

A simple Ulauncher extension to ask ChatGPT a question directly from the browser.

## Features

*   Opens `chatgpt.com` with your prompt pre-filled via the `q` query parameter.
*   Uses a configurable keyword (defaults to `gpt`).
*   Optionally, add an OpenAI API key to get the answer directly in Ulauncher's
    results list, without opening a browser.

## Installation

1.  Open Ulauncher's preferences.
2.  Go to the "Extensions" tab.
3.  Click "Add extension".
4.  Paste this URL into the input field: `https://github.com/Aad6552/Chatgpt-Search`
5.  Click the "Add" button.

## Usage

In Ulauncher, type `gpt` followed by a space and your prompt.

Example: `gpt explain quicksort in one sentence`

Then press Enter.

### Using the OpenAI API instead of the browser

By default, pressing Enter opens `chatgpt.com` in your browser with the prompt
pre-filled. If you'd rather get the answer straight in Ulauncher:

1.  Get an API key from https://platform.openai.com/api-keys.
2.  Open the extension's preferences in Ulauncher and paste the key into the
    "OpenAI API Key" field.
3.  (Optional) Set the "OpenAI Model" field to the model you want to use
    (defaults to `gpt-4o-mini`).

With a key set, typing `gpt <prompt>` and pressing Enter sends the prompt to
the OpenAI API and shows the answer as a result item. Press Enter again to
copy the full answer to the clipboard.

Note: this uses your own OpenAI account and API usage is billed by OpenAI
according to their pricing.

## Requirements
Your Chatgpt.com should be logged into your account.
