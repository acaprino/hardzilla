#!/usr/bin/env python3
"""
Base ViewModel
Foundation for all view models with observable properties
"""

from typing import Dict, Callable, Any, List


class BaseViewModel:
    """
    Base class for view models with property change notification.

    Implements the Observer pattern for UI reactivity.
    """

    def __init__(self):
        """Initialize with empty observers dictionary"""
        self._observers: Dict[str, List[Callable]] = {}
        self._properties: Dict[str, Any] = {}

    def subscribe(self, property_name: str, callback: Callable[[Any], None]) -> None:
        """
        Subscribe to property changes.

        Args:
            property_name: Name of property to observe
            callback: Function to call when property changes (receives new value)
        """
        if property_name not in self._observers:
            self._observers[property_name] = []
        self._observers[property_name].append(callback)

    def unsubscribe(self, property_name: str, callback: Callable[[Any], None]) -> None:
        """
        Unsubscribe from property changes.

        Args:
            property_name: Name of property
            callback: Callback to remove
        """
        if property_name in self._observers and callback in self._observers[property_name]:
            self._observers[property_name].remove(callback)

    def _notify(self, property_name: str, value: Any) -> None:
        """
        Notify all observers of a property change.

        Args:
            property_name: Name of property that changed
            value: New value
        """
        if property_name in self._observers:
            for callback in self._observers[property_name]:
                callback(value)

    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a property value"""
        return self._properties.get(name, default)

    def set_property(self, name: str, value: Any) -> None:
        """Set a property and notify observers"""
        old_value = self._properties.get(name)
        if old_value != value:
            self._properties[name] = value
            self._notify(name, value)
