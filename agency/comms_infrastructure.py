"""This file handles the various communication _mechanisms_ available to the channels."""

import logging
import os
import queue
import sys
from threading import Thread
from typing import List

#from agency.channel import ChannelParams
import agency

# import agency.channel # NOTE: apparently this avoids circular dependency issues since it's blank on import? (as opposed to from ... import ...)
# https://stackoverflow.com/questions/11698530/two-python-modules-require-each-others-contents-can-that-work

# NOTE: setting up a flask server is going to have to be a singleton thing, that way if someone specifies multiple rest endpoints, they're all handled by the
#   same server and we don't end up with one agent spawning 10 server instances.




# TODO: CommLinks can't block, but they need to have some "stay-alive-necessary" mechanism so that the main runnable doesn't exit while they are still active.


class CommLinkList:
    """A collection of active commlinks. This allows overarching management and global tx/rx to and from 
    all applicable commlinks in an intelligent (singleton-based where necessary) way. THIS is the rEaL function
    that handles scheduling and threading and keepalive etc."""

    
    def __init__(self):
        self.commlinks: List[CommLink] = []

        # TODO: list of timer threads for scheduled commlinks (maybe the targets should actually be a function on the commlink?)

        self.cli_in = []
        self.cli_out = [] # only applies to those with use_global specified. Just a fast way to index them.

        self.cli_rx_thread = None
        
        self.q = queue.Queue() # TODO: unclear if this is the correct place to put this

    def add_commlink(self, commlink):
        logging.debug("Adding commlink %s" % commlink)
        commlink_id = len(self.commlinks)
        self.commlinks.append(commlink)
        if type(commlink.rx_mechanism) == CLIMechanism:
            self.cli_in.append(commlink_id)
        if type(commlink.tx_mechanism) == CLIMechanism:
            self.cli_out.append(commlink_id)

        self.establish_mechanisms() # TODO: this is almost certainly not where this belongs

    def establish_mechanisms(self):
        logging.info("Establishing commlinklist mechanisms")
        if len(self.cli_in) > 0:
            logging.debug("We have an input CLI!")
            self.cli_rx_thread = Thread(target=self.cli_rx, args=[self.q])


    def tx(self, msg, params):
        ids, links = self.filter_tx_commlinks(params)

        print("cli_out", self.cli_out)
        print("ids", ids)

        for index in ids:
            if index in self.cli_out:
                # TODO: we only want to transmit out on cli once
                print(msg) # doooo we need something fancier than this? I don't think we can use an actual climechanism because input is all wonky if threaded.
                
    def begin_monitor_rx(self):
        """Commences all listening threads!"""
        logging.info("Comm link list beginning to monitor input commlinks")
        print(self.cli_in)

        # TODO: this doesn't necessarily work if one of the input channels allows the creation/setup of additional channels/commlinks...
        #   maybe instead of this funciton also handling closing of threads, we have a separate "loop" function while alive that can handle
        #   a queue of new things or something.

        # start listening to cli stdin
        if self.cli_rx_thread is not None:
            logging.debug("About to start cli rx thread")
            self.cli_rx_thread.start()


        # spawn anything else necessary

        
        # rejoin cli if called
        if self.cli_rx_thread is not None:
            self.cli_rx_thread.join()
            cli_input = self.q.get()
            # NOTE: alternatively instead of joining the thread we can just use self.q.get as a blocker

            # TODO: do we restart the thread? This should be based on keep-alive
            # TODO: keep alive should be based on a cli flag rather than having to explicitly specify this in agent or user channels

            # determine which threads were listening for CLI RX and distribute to approrpirate rx channels
            for commlink_id in self.cli_in:
                logging.debug("Running RX function for %s" % commlink_id)
                logging.debug("RX function is for %s" % self.commlinks[commlink_id])
                # STRT: rx_function really needs to take information about commlink/channel too.
                self.commlinks[commlink_id].rx_function("".join(cli_input), self.commlinks[commlink_id].local_channel, None) 
    

    def filter_tx_commlinks(self, params):
        """For a given set of channelparams, find all applicable commmlinks that can be used to transmit the message."""
        # TODO: (12/15/2021) wait, why does this work with only one set of params and not two again?
        logging.debug("Searching for available tx commlinks...")
        print("params to fit", params)
        applicable_ids = []
        applicable = []
        for i, commlink in enumerate(self.commlinks):
            print(commlink.local)
            print(commlink.local.fits(params))
            if commlink.local.direction != "rx" and commlink.local.fits(params):
                applicable_ids.append(i)
                applicable.append(commlink)
                
        logging.debug("Found %s" % len(applicable))
        return applicable_ids, applicable

        # NO NO NO. the establish makes sense in individual commlink, don't duplicate logic here. Determine what's needed
        # based on the actual mechanisms.
        #if commlink.local.medium == "cli":
            #self.cli_listen.append(commlink_id)


    def cli_rx(self, q):
        # TODO: (12/15/2021) rename q....
        # TODO: this probably needs to go into the mechanisms, but since (I think) only one thread can read from stdin at a time, 
        #   we have to have a single global rx
        # NOTE: this only gets "used"

        logging.debug("CLI_RX commlinklist thread is listening on stdin...")

        lines = []
        
        line = sys.stdin.readline() 
        while line != "\n":
            lines.append(line)
            line = sys.stdin.readline() 
        print("received lines", lines) # debug
        q.put(lines)
        #return lines
            

        # we join on a double new line TODO: need to determine if this is actually the best way or not



# TODO: we'll probably need information from the agent for this somehow? For config stuff. Careful of circular dependencies.
#   probably instead we should just pass in whatever info is needed
# does every commlink get set up in its own thread? [prob depends what type of channel it is]
class CommLink:
    """This is an established connection over a channel. This is where most of the logic for scheduling,
    message queuing etc. should take place."""
    def __init__(self, rx_function, local=None, target=None, local_channel=None):
        """Not using type info because circular, but local and target are ChannelParam types."""
        # TODO: we prob want to keep channel information in here
        self.local = local
        self.target = target
        self.rx_function = rx_function
        self.local_channel = local_channel # TODO: (12/15/2021) why is this "local" channel, the channel has both local and target, two channels would never make sense

        self.rx_mechanism: CommMechanism = None
        self.tx_mechanism: CommMechanism = None

        self.establish_mechanisms()

        # TODO: ensure a medium is specified?

    def __repr__(self):
        rep = "<"
        if self.local_channel is not None and self.local_channel.name is not None:
            rep += self.local_channel.name
        else:
            rep += "unnamed"

        if self.local.stream is not None:
            rep += f" '{self.local.stream}'"
        rep += f" rx:{self.rx_mechanism.__class__} tx:{self.tx_mechanism.__class__}>"
        return rep

    def establish_mechanisms(self):
        
        # TODO: check for one-directional web request/scrape RX
        
        
        # determine primarily by medium
        if self.local.medium == "cli":
            if self.local.direction == "tx":
                self.tx_mechanism = CLIMechanism()
            elif self.local.direction == "rx":
                self.rx_mechanism = CLIMechanism()
            else:
                self.tx_mechanism = CLIMechanism()
                self.rx_mechanism = CLIMechanism()
            

    def tx(self, msg):
        # TODO: similar 'establish' proc to rx? If we schedule an output, we have to handle the queuing and sending
        #   here, that's where the abstraction belongs.

        # testing only
        name = 'unnamed'
        if self.local_channel is not None:
            name = self.local_channel.name
        logging.debug("Commlink attempting to transmit message: '%s' (channel %s)" % (msg, name))
        self.tx_mechanism.tx(msg)

    def rx(self):
        # TODO: (12/12/2021) are we actually still doing this here? Or is this supersceded by commlinklist somehow? I think only supersceded if singletone mechanism?

        
        # this is where, based on local medium and activity, we either spin up a thread to spin wait or not?
        # so this handles activity, not the actual mechanism

        if self.local.activity == "scheduled":
            # TODO: or is this handled inside
            # TODO: we know we need timer stuff.
            pass

        # TODO: on rx, call rx_function
        
        pass



class CommMechanism:
    """Comm mechanisms specify the actual immediate code to use to send/receive data."""
    def __init__(self):
        pass

    def rx(self):
        pass

    def tx(self, content):
        pass


class CLIMechanism(CommMechanism):

    # TODO: this needs to be able to handle an endpoint and spawn the command and read/write stdout/stdin
    def __init__(self, use_global: bool = True):
        """If use_global is set to true, use the commlinklist's global singleton cli mechanism. This prevents a message
        from being printed to stdout multiple times if going through multiple commlinks. (However that may be desired 
        sometimes."""
        super().__init__()

    def tx(self, content):
        print(content) # derp :3


class FileMechanism(CommMechanism):
    def __init__(self, path: str, default_filename: str, encoding: str = None, append: bool = False):
        # default_filename is for if path is a directory rather than a specific file. (prob pass in agent name and streamname or similar)

        self.path = path
        self.default_filename = default_filename

        self.target_file = None
        self.resolve_target()
        
        super().__init__()

    def resolve_target(self):
        """Make sure necessary folders exist and ensure we have a filename."""
        if os.path.exists(self.path):
            if os.path.isdir(self.path):
                self.target_file = os.path.join(self.path, self.default_filename)
            else:
                self.target_file = self.path
        else:
            if self.path[-1] == "/":
                # it's a dir
                # ensure dirs existence
                # TODO: make dirs does not handle '..' so make sure to resolve to absolute: https://stackoverflow.com/questions/32838760/how-to-resolve-relative-paths-in-python
                os.makedirs(self.path, exist_ok=True)
                self.target_file = os.path.join(self.path, self.default_filename)
            else:
                # TODO: ensure path up till filename
                pass

    def rx(self):
        # TODO: what if it's a binary file? We'll need to set based on encoding passed
        with open(self.target_file, 'r') as infile:
            content = infile.read()
        return content

    def tx(self, content):
        with open(self.target_file, 'w') as outfile:
            outfile.write(content)
        


class WebRequestMechanism(CommMechanism):
    def __init__(self):
        super().__init__()

    def rx(self):
        pass

    def tx(self):
        pass


class FlaskServerMechanism(CommMechanism):
    pass
