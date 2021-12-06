import datetime
import json

import feedparser

import agency
from agency import Channel, ChannelParams

INFO = {"author": "Nathan", "name": "SynapseKWFinder"}


def process_feed(feed_str):
    """Take the string RSS and grab the entries of interest from it."""
    feed = feedparser.parse(feed_str)

    keyword = "synapse"
    output = []
    for entry in feed.entries:
        if keyword in entry.title.lower():
            output.append(
                {"title": entry.title, "link": entry.link, "summary": entry.summary}
            )

    output_json = json.dumps(output)
    # agency.tx(output_json, stream="entries", encoding="json") # TODO:


# TODO: at some point messages themselves need to probably have meta data, so a message needs a "payload"
#   which would be the actual rss dump itself.
def rx(message, channel, instance_config):
    print(f"Message received: {message} on channel {channel}")
    if channel.encoding == "rss":
        process_feed(message)


agency.init(INFO)


# TODO: at some point we're going to have to be able to define _sets_ of local/target options that go together, at that
#   point it will really make sense to be able to configure this outside of the agent script itself.
agency.define_channel(
    Channel(
        common=ChannelParams(stream="entries", encoding="json"),
        local=ChannelParams(direction="tx"),
        name="Output Entries"
    )
)
agency.define_channel(
    Channel(local=ChannelParams(direction="rx", stream="scrape", encoding="rss", name="RSS input")),
    #action=rx, # TODO:  
)


# agency.define_streams(["entries"]) #?????????
# NOTE: doesn't make sense for tx channel to have an action
# agency.define_channel(direction="tx", stream="entries", encoding="json")
# TODO: if you don't specify an action, it goes through default rx
# agency.define_channel(direction="rx", stream="scrape", encoding="rss", action=rx)

agency.rx(rx)  # TODO: is this necessary? Yes, yes it is
