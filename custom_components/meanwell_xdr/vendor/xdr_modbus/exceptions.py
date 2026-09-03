"""Exceptions raised by the XDR device library."""

from __future__ import annotations


class XdrError(Exception):
    """Base class for every error raised by this library."""


class XdrModelError(XdrError, ValueError):
    """The device reported a model string this library does not understand."""


class XdrValueValidationError(XdrError, ValueError):
    """A value passed to a write is outside the range the device accepts."""
