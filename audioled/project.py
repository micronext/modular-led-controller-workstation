import asyncio

from audioled.filtergraph import (FilterGraph, Updateable)0
from typing import List
import audioled.devices


class Project(Updateable):
    def __init__(self, name='Empty project', description='', device=None):
        self.slots = [None for i in range(127)]
        self.activeSlotId = 0
        self.name = name
        self.description = description
        self.id = None
        self.outputSlotMatrix = None
        self._previewDevice = device  # type: audioled.devices.LEDController
        self._previewDeviceIndex = 0
        self._contentRoot = None
        self._filterGraphForDeviceIndex = {}
        self._outputThreads = []  # type: typing.List

    def __cleanState__(self, stateDict):
        """
        Cleans given state dictionary from state objects beginning with _
        """
        for k in list(stateDict.keys()):
            if k.startswith('_'):
                stateDict.pop(k)
        return stateDict

    def __getstate__(self):
        """
        Default implementation of __getstate__ that deletes buffer, call __cleanState__ when overloading
        """
        state = self.__dict__.copy()
        self.__cleanState__(state)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        for slot in self.slots:
            if slot is not None:
                slot._project = self

    def setDevice(self, device: audioled.devices.MultiOutputWrapper):
        if not isinstance(device, audioled.devices.MultiOutputWrapper):
            raise RuntimeError("Device has to be MultiOutputWrapper")
        else:
            self._previewDevice = device._devices[self._previewDeviceIndex]
            self._devices = device._devices

    def update(self, dt, event_loop=asyncio.get_event_loop()):
        """Update active FilterGraph

        Arguments:
            dt {[float]} -- Time since last update
        """
        self.sendUpdateCommand()

        activeFilterGraph = self.getSlot(self.activeSlotId)
        if activeFilterGraph is not None:
            self.propagateNumPixelsFromConfig(activeFilterGraph)
            activeFilterGraph.update(dt, event_loop)

    def propagateNumPixelsFromConfig(self, activeFilterGraph: FilterGraph):
        # Propagate num pixels from server configuration
        if self._previewDevice is not None and activeFilterGraph.getLEDOutput() is not None:
            if (self._previewDevice.getNumPixels() != activeFilterGraph.getLEDOutput().effect.getNumOutputPixels()
                    or self._previewDevice.getNumRows() != activeFilterGraph.getLEDOutput().effect.getNumOutputRows()):
                print("propagating {} pixels on {} rows".format(self._previewDevice.getNumPixels(), self._previewDevice.getNumRows()))
                activeFilterGraph.propagateNumPixels(self._previewDevice.getNumPixels(), self._previewDevice.getNumRows())

    def sendUpdateCommand(self):
        # TODO: Implement
        pass

    def process(self):
        """Process active FilterGraph
        """
        activeFilterGraph = self.getSlot(self.activeSlotId)
        if activeFilterGraph is not None:
            if self._previewDevice is not None and activeFilterGraph.getLEDOutput() is not None:
                activeFilterGraph.process()
                if activeFilterGraph.getLEDOutput()._outputBuffer[0] is not None and self._previewDevice is not None:
                    self._previewDevice.show(activeFilterGraph.getLEDOutput()._outputBuffer[0])

    def setFiltergraphForSlot(self, slotId, filterGraph):
        print("Set {} for slot {}".format(filterGraph, slotId))
        if isinstance(filterGraph, FilterGraph):
            filterGraph._project = self
            self.slots[slotId] = filterGraph

    def activateScene(self, sceneId):
        """Activates a scene

        Scene: Project Slot per Output Device
        """
        # Update _filterGraphForDeviceIndex
        dIdx = 0
        for device in self._devices:
            # Get filterGraph for slot Id associated with this device
            slotId = self.outputSlotMatrix[dIdx]
            filterGraph = self.getSlot(slotId)
            # Make copy of this filtergraph
            # TODO: Revise?
            
            dIdx+=1


    def previewSlot(self, slotId, deviceId):
        # TODO: Separate preview slot and active slot
        self.activeSlotId = slotId
        print("Activate slot {} with {}".format(slotId, self.slots[slotId]))
        return self.getSlot(slotId)

    def getSlot(self, slotId):
        if self.slots[slotId] is None:
            self.slots[slotId] = FilterGraph()
        return self.slots[slotId]