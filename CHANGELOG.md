# Changelog

## v1.0.1

### Fixed
- AssertIntegerConverterService did accidentally also convert Waves fees. This has been changed.
Waves fees are not converted anymore.

## v1.0.2

### Added
- Adds *copy to clipboard button* in the web view. It establishes
a convenient way to copy the coin address

### Fixed

- Transactions are no longer processed in parallel because
users have reported strange issues with that
- Fixed problem that Firefox users were not able to copy the generated coin address
