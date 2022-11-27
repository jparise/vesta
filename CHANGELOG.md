# Changelog

## 0.9.0 - Not yet released
### Changed
- Switched to [HTTPX](https://www.python-httpx.org/) as the underlying HTTP library.

## 0.8.0 - 2022-08-13
### Added
- `LocalClient` provides a client interface to Vestaboard's Local API.
- `ReadWriteClient` provides a client interface to Vestaboard's Read / Write API.

### Changed
- The documentation now uses the [Furo theme](https://github.com/pradyunsg/furo).
- [Requests](https://requests.readthedocs.io/) version 2.27.0 or later is now required.

## 0.7.3 - 2022-05-31
### Added
- Various typing improvements, including a `py.typed` marker file.

## 0.7.2 - 2021-12-30
### Added
- `encode_text()`'s `valign` argument can be set to `None` to disable row
  padding.

### Changed
- `encode()`'s error handling has been improved. A `ValueError` will now
  be raised for all unsupported character codes, including those within the
  [0, 69] range such as 57, 58, and 61.

## 0.7.1 - 2021-12-19
### Fixed
- `encode_text()` was adding a leading blank character to the row after a line
  break.

## 0.7.0 - 2021-12-19
### Added
- `encode_text()` offers a `valign` argument for controlling vertical alignment
  within the board.
- `Client.post_message()` now raises ValueError if `message` is a list of
  encoded characters with the wrong dimensions. 

### Changed
- `encode_text()` now always produces six rows of output (a full board).

### Removed
- Dropped support for Python 3.6, which has officially reached the end of its
  supported life.

## 0.6.0 - 2021-12-05
### Added
- `encode_text()` for encoding lines of text

### Fixed
- Fix space character encoding

## 0.5.1 - 2021-11-06
### Added
- Initial Sphinx-based documentation

## 0.5.0 - 2021-11-01
- Initial release
