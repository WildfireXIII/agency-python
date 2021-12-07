import argparse
import logging
from typing import List
import sys

from agency.channel import Channel, ChannelParams, ChannelList
from agency.comms_infrastructure import CommLink, CommLinkList

# NOTE: making the decision now - logging does not have to be interoperable (just has to be text based), **metrics do**

# required default channels:
# - log (tx)
# - metrics (tx)
# - agent info (tx) NO. this is a stream, not a channel?
# - meta command (rx)
# - channel list (tx) NO. This is a stream not a channel?
# - request (rx)
# - query (rx/tx)

# - broadcast "callsign" :D (tx) - no this probably needs to be handled some other way  (like having a central registration agent that when you spawn each new agent it auto creates a connection to or something)

# - memory? (rx/tx) god no
# - config? (rx) NO. yes?


def set_default_channels(agent):
    # NOTE: an unlisted channel means it's ephemeral/only lives for a single agent "spawn" session. Ideal for CLI channel.
    #agent.define_channel(stream="command", medium="CLI", unlisted=True)
    #agent.define_channel(stream="query", medium="CLI")



    ai_tx = Channel(local=ChannelParams(stream="agent-info", direction="tx"), name="AUTO-agent-info-output")
    m_tx = Channel(local=ChannelParams(stream="metrics", direction="tx", medium="cli"), name="AUTO-metrics-output")
    cl_tx = Channel(local=ChannelParams(stream="channel-list", direction="tx"), name="AUTO-channel-list-output")


    agent.define_channel(ai_tx)
    agent.define_channel(m_tx)
    agent.define_channel(cl_tx)
    
    
    # connect all CLI outputs???? to active commandline
    #all_cli = Channel(common=ChannelParams(medium="cli"))
    # TODO: assume channel definitions are _not_ reversed when calling connect. Everything is from perspective of active agent.
    ai_rx = Channel(common=ChannelParams(medium="cli"), local=ChannelParams(stream="agent-info"), target=ChannelParams(direction="rx"), temporary=True)
    # NOTE: the target above should be implicit??
    m_rx = Channel(common=ChannelParams(medium="cli"), local=ChannelParams(stream="metrics"), temporary=True)
    all_rx = Channel(common=ChannelParams(medium="cli"), temporary=True) # NOTE: this is probably an issue because....I don't know
    
    agent.connect(ai_rx)
    agent.connect(m_rx)
    agent.connect(all_rx)

    
    # define a **connection** that is CLI to CLI (for testing purposes)
    test_tx = Channel(common=ChannelParams(stream="test-echo", medium="cli"), name="AUTO-test-echo")
    agent.define_connection(test_tx)
    def echo_response(msg):
        logging.info("We have receieved a test-echo message '%s'" % msg)
        tx(msg, stream='test-echo', medium='cli')
    agent.connect(Channel(common=ChannelParams(stream="test-echo", medium="cli")), echo_response)
    

# class: instance? (this could handle memory/config stuff)

AGENT = None

# TODO: add ability to add in custom agent hooks inside your script code?

class Agent:
    def __init__(self):
        self.channel_list: ChannelList = ChannelList()
        self.commlinks: List[CommLink] = CommLinkList() # TODO: might want to make this a class like channellist too for easy querying and storage.
        self.default_rx = None

        self.msg_history = []


    def determine_runmode(self):
        """Figure out based on the channellist whether we need to be running a server, a timer, or just a cli."""
        pass

    
    def query(self, message):
        pass
    

    def meta_command(self, message):
        """Handle CLI default meta commands."""
        pass


    def define_channel(self, channel: Channel):
        self.channel_list.add_channel(channel)

    def connect(self, channel: Channel, rx_function = None):
        if rx_function is None:
            rx_function = self.default_rx
        new_commlinks = self.channel_list.connect(channel, rx_function)
        self.commlinks.extend(new_commlinks)

    def tx(self, msg, params: ChannelParams):
        #applicable = self.resolve_applicable_commlinks(params)
        self.msg_history.append(msg)
        msg_index = len(self.msg_history) # TODO: make more sophisticated when storag/memory implemented

        self.commlinks.tx(msg, params)
        
        #for commlink in applicable:
            #commlink.tx(msg)

    # def resolve_applicable_commlinks(self, params: ChannelParams) -> List[CommLink]:
    #     logging.debug("Searching for applicable commlinks...")
    #     applicable = []
    #     for commlink in self.commlinks:
    #         if commlink.local.direction == "tx" and commlink.local.fits(params):
    #             applicable.append(commlink)

    #     logging.debug("Found %s" % len(applicable))
    #     return applicable


def init(agent_info):
    global AGENT
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s', level=logging.DEBUG, stream=sys.stdout)
    logging.info("Global agent activation requested")
    AGENT = Agent()
    
    #parser = argparse.ArgumentParser()


def define_channel(channel: Channel):
    AGENT.define_channel(channel)


def tx(msg, **kwargs):
    logging.debug("Transmitting message '%s'" % msg)
    params = ChannelParams(**kwargs)
    AGENT.tx(msg, params)


def rx(action_f):
    """The 'deploy' command, this sets the _default_ action function, and establishes the default channels."""
    
    AGENT.default_rx = action_f
    set_default_channels(AGENT) 
    #tx("THIS IS A TEST", medium="cli")
    tx("THIS IS A TEST", medium="cli", stream="agent-info")

