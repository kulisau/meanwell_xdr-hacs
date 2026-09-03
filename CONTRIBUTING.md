# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## GitHub is used for everything

GitHub is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using `scripts/lint`).
4. Test your contribution.
5. Issue that pull request!

## Any contributions you make will be under the Apache-2.0 License

In short, when you submit code changes, your submissions are understood to be under the same [Apache-2.0 license](http://choosealicense.com/licenses/apache-2.0/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## The vendored device library

`custom_components/meanwell_xdr/vendor/xdr_modbus` is a verbatim copy of the
[`xdr-modbus`](https://github.com/kulisau/xdr-modbus) device library. Fix
device-model bugs there first and re-vendor the package; do not patch the
vendored copy in place.
