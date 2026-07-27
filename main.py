from urllib.parse import quote
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

# Main Extension Class
class ChatGPTExtension(Extension):

    def __init__(self):
        super().__init__()
        # Subscribe to the KeywordQueryEvent
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

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

        # Construct the ChatGPT URL with the prompt pre-filled
        search_url = f"https://chatgpt.com/?q={quote(query)}"

        # Create the result item to display in Ulauncher
        item = ExtensionResultItem(
            icon='images/icon.png',
            name=f"Ask ChatGPT: '{query}'",
            description="Open ChatGPT with your prompt in your browser",
            on_enter=OpenUrlAction(search_url)
        )

        return RenderResultListAction([item])

# Run the extension
if __name__ == '__main__':
    ChatGPTExtension().run()
