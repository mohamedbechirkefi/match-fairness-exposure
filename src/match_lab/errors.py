# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Explicit error types. Every rejected input raises one of these, never a bare assert."""


class MatchLabError(Exception):
    """Base class for all MATCH errors."""


class InvalidInputError(MatchLabError, ValueError):
    """An argument is out of its documented domain."""


class InvalidMatchingError(MatchLabError):
    """A matching violates a validity invariant (duplicate, capacity, inconsistency)."""


class SchemaError(MatchLabError):
    """A result, manifest or config document does not match its versioned schema."""


class ProtocolNotFrozenError(MatchLabError):
    """A confirmatory run was requested while the protocol is not frozen (G-FREEZE)."""
