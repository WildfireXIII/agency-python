"""Module for handling agent wrapper code."""

import logging
import sys

from agency.trigger import Trigger

ACTIVE_AGENT = None


class Agent:
    def __init__(self, name):
        self.actions = {}
        self.triggers = []
        self.name = name

        logging.info("Initializing agent '%s'" % self.name)

    def register_action(self, f, action_name: str):
        self.actions[action_name] = self.wrap_action(f, action_name)

    def register_trigger(self, trigger: Trigger, action_name: str):
        if action_name not in self.actions.keys():
            raise Exception(f"The action name {action_name} hasn't been registered for this agent.")
        trigger.action_f = self.actions[action_name]
        self.triggers.append(trigger)


    def wrap_action(self, f, action_name: str):
        """Sort of like a decorator but not really. This is how we're handling all of the meta
        stuff for the actions. Not using a decorator for now because I prefer how the example looks
        as is, and I think using decorators might break with some of this being class-based."""
        def wrapped_f(trigger_name, trigger_input):
            logging.info("TRIGGER - Agent: %s, Action: %s, Trigger: %s" % (self.name, action_name, trigger_name))
            # TODO: Log the environment info!
            # TODO: Log all of the things!
            # TODO: Store organized metrics about trigger type and time
            return f(trigger_name, trigger_input)
            # TODO: Log the end of the action!
            # TODO: Store organized metrics about the action runtime, output success/failure
        return wrapped_f

    # TODO: for determining "liveness" of an agent, we could store process ID and use OS calls to see if that ID is running? (for singleton agents) Blasdlfsd;lfkjasdf there needs to be a way to allow communication from CLI to a running agent without necessarily starting up a _new_ agent. Unsure best way to handle this, but I'm again tempted to offload the complexity into the communications aspect of the protocol.


    def deploy(self):
        # TODO: yeah this clearly doesn't work if activate is blocking...
        # TODO: each trigger is going to have to run in own thread. (For once this would actually
        #   an okay use for default python multithreading since performance isn't likely going to
        #   be the issue here.
        for trigger in self.triggers:
            trigger.activate()


def global_agent_check():
    if ACTIVE_AGENT is None:
        raise Exception("Global agent is not active. Try calling agency.init()")


def register_action(f, action_name: str):
    global_agent_check()
    
    logging.info("Registering action '%s' with global agent..." % action_name)
    ACTIVE_AGENT.register_action(f, action_name)


def register_trigger(trigger: Trigger, action_name: str):
    global_agent_check()
    
    logging.info("Registering trigger of type '%s' for action '%s' with global agent..." % (trigger.typename, action_name))
    ACTIVE_AGENT.register_trigger(trigger, action_name)


def cli_deploy():
    global_agent_check()
    logging.info("Deploying global agent...")
    ACTIVE_AGENT.deploy()
    # TODO: Inject CLI argparse stuff for statusy things


def init(agent_name):
    global ACTIVE_AGENT
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s', level=logging.DEBUG, stream=sys.stdout)
    logging.info("Global agent activation requested")
    ACTIVE_AGENT = Agent(agent_name)
    # TODO: init logging
