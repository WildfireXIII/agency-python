import datetime
import json
import logging
import os
from typing import Dict

import feedparser

import agency

PREVIOUS_CACHE = "./cache/previous_entries.json"  # stores all entries from last scrape
NEW_CACHE = "./cache/new_entries.json"  # stores the new entries in the last scrape (wrt to the scrape before that)
DEBUG_SCRAPE = "./cache/scrape"  # prefix for raw feed scrape


def dump_scrape(feed: Dict):
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    scrape_name = f"{DEBUG_SCRAPE}_{now}.json"

    with open(scrape_name, "w") as outfile:
        json.dump(feed, outfile, default=lambda x: str(x))


# [A] if we did this all OOP like, this function could be called with the action object for additional info...how translateable is that between languages though?
# note that we could also pass in some sort of dictionary "store" for locally storing metrics, see google doc
# TODO: why don't we just pass the trigger object?
def grab_matrix_feed(trigger_name: str, trigger_input):
    """The primary action for this agent."""
    logging.info("I got called via %s trigger!" % trigger_name)
    logging.info("Trigger input: %s" % trigger_input)

    # scrape the RSS
    feed = feedparser.parse("https://matrix.org/blog/feed")
    dump_scrape(feed)

    # make sure we got something
    if feed.status != 200:
        raise Exception(f"Feed URL returned non-200 status code: {feed.status}")

    # load any previous entries from disk
    previous_entries = []
    if os.path.exists(PREVIOUS_CACHE):
        logging.debug(
            "Previous entries found, loading from cache: '%s'..." % PREVIOUS_CACHE
        )
        with open(PREVIOUS_CACHE, "r") as infile:
            previous_entries = json.load(infile)
            logging.debug(f"Loaded {len(previous_entries)} entries")

    # check for any differences
    new_entries = []
    if feed.entries != previous_entries:
        logging.info("We done found some new blood!")

        # write out the new data to cache
        with open(PREVIOUS_CACHE, "w") as outfile:
            logging.debug("Writing out updated entries to cache.")
            json.dump(feed.entries, outfile)

        # determine which stories are new
        logging.debug("Sorting through to find new entries")
        for entry_a in feed.entries:
            found = False
            for entry_b in previous_entries:
                if entry_a["id"] == entry_b["id"]:
                    found = True
                    break
            if not found:
                new_entries.append(entry_a)
                logging.debug("Story %s is new!" % entry_a["title"])

    else:
        logging.info("Nope, same old same old")

    # TODO - what do we actually return to "make this a trigger" or to communicate with other agents?
    return new_entries


# TODO: how do we handle configuration? Per agent? Is each agent given some sort of json config?
agency.init("matrix_blog_scraper")
# via [A], we could technically have register_action return a fancy action object
agency.register_action(grab_matrix_feed, "grab_matrix_feed")
agency.register_trigger(agency.trigger.Timer("10s", "basic timer"), "grab_matrix_feed")
agency.cli_deploy()
