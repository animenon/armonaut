<!---
Add all non-trivial changes to this list along with your
name, the change type, the pull request number, issue number,
and issue reporter if applicable. Make sure to add hyperlinks for
issue and pull request numbers.
-->

# Changelog

All notable changes to Armonaut will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)
with additional versioning for beta features as recommended by
[Python Packaging Guidelines](https://packaging.python.org/tutorials/distributing-packages/#choosing-a-versioning-scheme).

## 1.0.0b1

- Create initial models for builds.
- Implement rate-limiting for the API endpoints
- Create the `GET /api/v1/projects/<host>/<owner>/<name>` API endpoint.
- Create the `GET /api/v1/projects/<host>/<owner>/<name>/builds` API endpoint
- Create the `GET /api/v1/projects/<host>/<owner>/<name>/builds/<build_number>` API endpoint
- Create the `GET /api/v1/projects/<host>/<owner>/<name>/branches` API endpoint
- Frontend template using Bootstrap and Backbone.js
