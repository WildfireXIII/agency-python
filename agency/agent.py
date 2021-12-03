import argparse
from typing import List

from agency.channel import Channel, ChannelParams, ChannelList

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

    # TODO: define a **connection** that is CLI to CLI


    ai_tx = Channel(local=ChannelParams(stream="agent-info", direction="tx"))
    m_tx = Channel(local=ChannelParams(stream="metrics", direction="tx", medium="cli"))
    cl_tx = Channel(local=ChannelParams(stream="channel-list", direction="tx"))

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
    

# class: instance? (this could handle memory/config stuff)

AGENT = None


class Agent:
    def __init__(self):
        self.channel_list: ChannelList = ChannelList()


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
        pass

    def connect(self, channel: Channel):
        # RESOLVE.
        self.channel_list.connect(channel)


def init(agent_info):
    global AGENT
    AGENT = Agent()
    
    #parser = argparse.ArgumentParser()
    set_default_channels(AGENT) # TODO:  er....so this needs to go in RX, not in init


def define_channel(channel: Channel):
    AGENT.define_channel(channel)


def tx():
    pass


def rx(action_f):
    """The 'deploy' command, this sets the _default_ action function, and establishes the default channels."""
    
    # TODO: 
    pass

