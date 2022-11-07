"""Module for abstracting and implementing different types of triggers."""
import logging
import time


class Trigger:
    def __init__(self, typename, name):
        self.typename = typename
        self.name = name
        self.action_f = None
        
        logging.info("Trigger '%s' initialized" % name)

    def activate(self):
        """Run whatever logic is necessary to determine whether this triggers or not."""
        # NOTE: so this should presumably be blocking? How do we design actual server agents
        # with this in mind?
        pass


class Timer(Trigger):
    def __init__(self, time_string, name):
        # TODO: abstract this into function
        self.time_string = time_string
        self.delay = 0

        time_value = time_string[:-1]
        time_unit = time_string[-1]
        if time_unit == "s":
            self.delay = int(time_value)
        elif time_unit == "m":
            self.delay = int(time_value) * 60

        logging.info("Initializing timer trigger with delay value of '%s'" % self.delay)

        super().__init__("timer", name)

    def activate(self):
        logging.info("Activating timer '%s'" % self.name)
        # TODO: obviously bad.
        while True:
            logging.info("Sleeping %s seconds..." % self.delay)
            time.sleep(self.delay)
            self.action_f(self.name, {})
