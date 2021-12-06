"""This file handles the various communication _mechanisms_ available to the channels."""

import logging
import os

#from agency.channel import ChannelParams
import agency

# import agency.channel # NOTE: apparently this avoids circular dependency issues since it's blank on import? (as opposed to from ... import ...)
# https://stackoverflow.com/questions/11698530/two-python-modules-require-each-others-contents-can-that-work

# NOTE: setting up a flask server is going to have to be a singleton thing, that way if someone specifies multiple rest endpoints, they're all handled by the
#   same server and we don't end up with one agent spawning 10 server instances.




# TODO: CommLinks can't block, but they need to have some "stay-alive-necessary" mechanism so that the main runnable doesn't exit while they are still active.





# TODO: we'll probably need information from the agent for this somehow? For config stuff. Careful of circular dependencies.
#   probably instead we should just pass in whatever info is needed
# does every commlink get set up in its own thread? [prob depends what type of channel it is]
class CommLink:
    """This is an established connection over a channel. This is where most of the logic for scheduling,
    message queuing etc. should take place."""
    def __init__(self, rx_function, local=None, target=None, local_channel=None):
        """Not using type info because circular, but local and target are ChannelParam types."""
        self.local = local
        self.target = target
        self.rx_function = rx_function
        self.local_channel = local_channel

        self.rx_mechanism: CommMechanism = None
        self.tx_mechanism: CommMechanism = None

        self.establish_mechanisms()

        # TODO: ensure a medium is specified?

    def establish_mechanisms(self):
        tx_params = None
        if self.local.direction == "tx":
            tx_params = self.local

        if tx_params is not None and tx_params.medium == "cli":
            self.tx_mechanism = CLIMechanism()

            

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
        # this is where, based on local medium and activity, we either spin up a thread to spin wait or not?
        # so this handles activity, not the actual mechanism

        if self.local.activity == "scheduled":
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
    # TODO: this needs to be singleton
    def __init__(self):
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
