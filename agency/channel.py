import copy
import logging
from dataclasses import dataclass
from typing import List

import pandas as pd

from agency.comms_infrastructure import CommLink

PARAM_ATTRS = ["direction", "stream", "encoding", "medium", "activity", "schedule", "name", "endpoint"]


@dataclass
class ChannelParams:
    direction: str = None
    stream: str = None
    encoding: str = None
    medium: str = None
    activity: str = None
    schedule: str = None
    name: str = None
    endpoint: str = None

    def fits(self, other_params):
        """This determines "compatability" between the given channels."""
        # TODO: surely there's a way to do this with _get_attr
        # TODO: write unit tests for this

        # two channelparam sets are incompatible if there's anything that is _specified_ by both and is specified _differently_.
        for attr in PARAM_ATTRS:
            a = getattr(self, attr)
            b = getattr(other_params, attr)
            if a is not None and b is not None and a != b:
                return False
        return True

    def resolve(self, other_params):
        """Combines this paramset with another, taking the aspects of both and putting into one."""

        # NOTE: we should only be resolving two channel params that fit

        resolved = copy.deepcopy(self)

        for attr in PARAM_ATTRS:
            a = getattr(resolved, attr)
            b = getattr(other_params, attr)

            if a is None and b is not None:
                setattr(resolved, attr, b)
                
        return resolved

# NOTE: when channel local direction is "TX", then the target, if specified, is information for how another agent can receive it?

class Channel:
    def __init__(
        self,
        common: ChannelParams = None,
        local: ChannelParams = None,
        target: ChannelParams = None,
        temporary=False,
        name: str = None,
        # TODO: rx function as applicable
    ):
        self.common = common
        self.local = local
        self.target = target
        self.temporary = temporary
        self.name = name

    # def connect(self, channel: Channel):
    # pass

    def fits(self, channel):
        if (
                (self.common is None or channel.common is None or self.common.fits(channel.common))
                and (self.common is None or channel.local is None or self.common.fits(channel.local))
                and (self.common is None or channel.target is None or self.common.fits(channel.target))
                and (self.local is None or channel.local is None or self.local.fits(channel.local))
                and (self.target is None or channel.target is None or self.target.fits(channel.target))):
            return True
        return False


    def resolve(self, channel):
        """Return a resolved local and target channel params."""

        # resolve the two commons
        resolved_common = None
        if self.common is None and channel.common is not None:
            resolved_common = channel.common
        elif self.common is not None and channel.common is None:
            resolved_common = self.common
        elif self.common is not None and channel.common is not None:
            resolved_common = self.common.resolve(channel.common)

        # resolve the two locals
        resolved_local = None
        if self.local is None and channel.local is not None:
            resolved_local = channel.local
        elif self.local is not None and channel.local is None:
            resolved_local = self.local
        elif self.local is not None and channel.local is not None:
            resolved_local = self.local.resolve(channel.local)

        # resolve the two targets
        resolved_target = None
        if self.target is None and channel.target is not None:
            resolved_target = channel.target
        elif self.target is not None and channel.target is None:
            resolved_target = self.target
        elif self.target is not None and channel.target is not None:
            resolved_target = self.target.resolve(channel.target)

        # resolve local and target with common if applicable
        if resolved_common is not None and resolved_local is not None:
            resolved_local = resolved_local.resolve(resolved_common)
        if resolved_common is not None and resolved_target is not None:
            resolved_target = resolved_target.resolve(resolved_common)

        # if there is no local or no target, we assume it to be the resolved common (if there is one
        if resolved_local is None and resolved_common is not None:
            resolved_local = resolved_common
        if resolved_target is None and resolved_common is not None:
            resolved_target = resolved_common
            
        return resolved_local, resolved_target

    def __repr__(self):
        return f"common: {self.common}\nlocal: {self.local}\ntarget: {self.target}\ntemporary: {self.temporary}"

    


# NOTE: so actually using a connection requires at a minimum: the medium.

# TODO: still not seeing how to define a connection as being broadcast/rx-only or bidirectional? Sometimes we really only need one endpoint.


class ChannelList:
    def __init__(self):
        self.channels: List[Channel] = []

    def add_channel(self, channel: Channel):
        self.channels.append(channel)

    def connect(self, channel: Channel, rx_function) -> List[CommLink]:
        established = []
        
        for local_channel in self.channels:
            
            if local_channel.fits(channel):
                # TODO: do we just assume (and eventually check/throw exceptions) for non-conflicting params in common/local/target?
                # resolve to two ChannelParams instances
                #local = channel.local
                
                local, target = local_channel.resolve(channel)
                print(f"RESOLVED:\nlocal:{local}\ntarget:{target}\n\n\n")
                established.append(CommLink(rx_function, local, target, local_channel=local_channel))
            else:
                #print("nope :(\n\n")
                pass
            
            # if (
            #     (local_channel.common is not None and channel.common is not None and local_channel.common.fits(channel.common))
            #     and (local_channel.common is not None and channel.local is not None and local_channel.common.fits(channel.local))
            #     and (local_channel.common is not None and channel.target is not None and local_channel.common.fits(channel.target))
            #     and (local_channel.local is not None and channel.local is not None and local_channel.local.fits(channel.local))
            #     and (local_channel.target is not None and channel.target is not None and local_channel.target.fits(channel.target))
            # ):
            #     print("#### It fits!!!\n\n")
            # else:
            #     print("nope :(\n\n")
        return established
