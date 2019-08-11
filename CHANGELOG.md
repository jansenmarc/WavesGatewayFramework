# Changelog

## v1.0.5
- Hotfix for Pip dependency resolvement issues (https://github.com/jansenmarc/WavesGatewayFramework/issues/26)

## v1.0.4

### Bugfixes
- Adjustments for changed PyWaves behavior. See: https://github.com/jansenmarc/WavesGatewayFramework/issues/20

## v1.0.3

### Added
- Adds option *waves_chain_id* in the Gateway class constructor that
may be used to ovewrite the third parameter that the Gateway overhands
to the setNode function of pywaves.

## v1.0.2

### Added
- Adds *copy to clipboard button* in the web view. It establishes
a convenient way to copy the coin address

### Fixed

- Transactions are no longer processed in parallel because
users have reported strange issues with that
- Fixed problem that Firefox users were not able to copy the generated coin address

## v1.0.1

### Fixed
- AssertIntegerConverterService did accidentally also convert Waves fees. This has been changed.
Waves fees are not converted anymore.
