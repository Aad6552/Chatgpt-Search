import json
import urllib.error
import urllib.request
from urllib.parse import quote

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


# Main Extension Class
class ChatGPTExtension(Extension):

    def __init__(self):
        super().__init__()
        # Subscribe to the KeywordQueryEvent
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


def ask_openai(api_key, model, prompt):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    request = urllib.request.Request(
        OPENAI_API_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"].strip()


# Listener for the KeywordQueryEvent
class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # Get the query from the user
        query = event.get_argument()

        # If there's no query yet, show a placeholder message
        if not query:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='Ask ChatGPT',
                                    description='Enter your prompt...',
                                    on_enter=None)
            ])

        api_key = extension.preferences.get('openai_api_key', '').strip()

        # Construct the ChatGPT URL with the prompt pre-filled
        search_url = f"https://chatgpt.com/?q={quote(query)}"
        browser_item = ExtensionResultItem(
            icon='images/icon.png',
            name=f"Ask ChatGPT: '{query}'",
            description="Open ChatGPT with your prompt in your browser",
            on_enter=OpenUrlAction(search_url)
        )

        if not api_key:
            return RenderResultListAction([browser_item])

        api_item = ExtensionResultItem(
            icon='images/icon.png',
            name=f"Ask ChatGPT (API): '{query}'",
            description="Press Enter to get an answer from the OpenAI API",
            on_enter=ExtensionCustomAction(query, keep_app_open=True)
        )

        return RenderResultListAction([api_item, browser_item])


# Listener for the ItemEnterEvent, triggered when an OpenAI API request is submitted
class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_data()
        api_key = extension.preferences.get('openai_api_key', '').strip()
        model = extension.preferences.get('openai_model', '').strip() or 'gpt-4o-mini'

        try:
            answer = ask_openai(api_key, model, query)
            item = ExtensionResultItem(
                icon='images/icon.png',
                name=answer[:100] + ('…' if len(answer) > 100 else ''),
                description="Enter to copy the full answer to the clipboard",
                on_enter=CopyToClipboardAction(answer)
            )
        except urllib.error.HTTPError as e:
            if e.code == 401:
                message = "Invalid OpenAI API key. Check it in the extension preferences."
            elif e.code == 429:
                message = "Rate limit or quota exceeded on your OpenAI account."
            else:
                message = f"OpenAI API error ({e.code}): {e.reason}"
            item = ExtensionResultItem(
                icon='images/icon.png',
                name="Couldn't get an answer from OpenAI",
                description=message,
                on_enter=None
            )
        except urllib.error.URLError as e:
            item = ExtensionResultItem(
                icon='images/icon.png',
                name="Couldn't reach the OpenAI API",
                description=str(e.reason),
                on_enter=None
            )
        except Exception as e:
            item = ExtensionResultItem(
                icon='images/icon.png',
                name="Something went wrong",
                description=str(e),
                on_enter=None
            )

        return RenderResultListAction([item])


# Run the extension
if __name__ == '__main__':
    ChatGPTExtension().run()
