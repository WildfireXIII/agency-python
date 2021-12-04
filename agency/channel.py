import logging
from dataclasses import dataclass
from typing import List

import pandas as pd


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

    def fits(self, obj):
        """This determines "compatability" between the given channels."""
        # TODO: surely there's a way to do this with _get_attr
        # TODO: write unit tests for this
        if (
            self.direction is not None
            and obj.direction is not None
            and self.direction != obj.direction
        ):
            return False
        if (
            self.stream is not None
            and obj.stream is not None
            and self.stream != obj.stream
        ):
            return False
        if (
            self.encoding is not None
            and obj.encoding is not None
            and self.encoding != obj.encoding
        ):
            return False
        if (
            self.medium is not None
            and obj.medium is not None
            and self.medium != obj.medium
        ):
            return False
        if (
            self.activity is not None
            and obj.activity is not None
            and self.activity != obj.activity
        ):
            return False
        if (
            self.schedule is not None
            and obj.schedule is not None
            and self.schedule != obj.schedule
        ):
            return False
        if self.name is not None and obj.name is not None and self.name != obj.name:
            return False
        if (
            self.endpoint is not None
            and obj.endpoint is not None
            and self.endpoint != obj.endpoint
        ):
            return False
        return True


class Channel:
    def __init__(
        self,
        common: ChannelParams = None,
        local: ChannelParams = None,
        target: ChannelParams = None,
        temporary=False,
    ):
        self.common = common
        self.local = local
        self.target = target
        self.temporary = temporary

    # def connect(self, channel: Channel):
    # pass

    def fits(self, channel):
        print("self common fits common: ", end="")
        print((self.common is None or channel.common is None or self.common.fits(channel.common)))
        print("self common fits local: ", end="")
        print((self.common is None or channel.local is None or self.common.fits(channel.local)))
        print("self common fits target: ", end="")
        print((self.common is None or channel.target is None or self.common.fits(channel.target)))
        print("self local fits local: ", end="")
        print((self.local is None or channel.local is None or self.local.fits(channel.local)))
        print("self target fits target: ", end="")
        print((self.target is None or channel.target is None or self.target.fits(channel.target)))
        
        if (
                (self.common is None or channel.common is None or self.common.fits(channel.common))
                and (self.common is None or channel.local is None or self.common.fits(channel.local))
                and (self.common is None or channel.target is None or self.common.fits(channel.target))
                and (self.local is None or channel.local is None or self.local.fits(channel.local))
                and (self.target is None or channel.target is None or self.target.fits(channel.target))):
            return True
        return False

    def __repr__(self):
        return f"common: {self.common}\nlocal: {self.local}\ntarget: {self.target}\ntemporary: {self.temporary}"


# NOTE: so actually using a connection requires at a minimum: the medium.

# TODO: still not seeing how to define a connection as being broadcast/rx-only or bidirectional? Sometimes we really only need one endpoint.
class CommLink:
    def __init__(self, rx_function, local: ChannelParams = None, target: ChannelParams = None):
        pass

    


class ChannelList:
    def __init__(self):
        self.channels: List[Channel] = []

    def add_channel(self, channel: Channel):
        self.channels.append(channel)

    def connect(self, channel: Channel):
        print("#################### Attempting new connection #####################")
        for local_channel in self.channels:
            print("Comparing connecting channel")
            print(channel)
            print("with self:")
            print(local_channel)
            
            if local_channel.fits(channel):
                print("#### It fits!!!\n\n")
            else:
                print("nope :(\n\n")
            
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
