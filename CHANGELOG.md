# Changelog

## 0.7.0 - 2021-12-19
### Added
- `encode_text()` offers a `valign` argument for controling vertical alignment
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
