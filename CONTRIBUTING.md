Contributing
============

Thank you for considering contributing to this project. *geoclaw-landspil* is an
open-source project hosted on GitHub at
https://github.com/barbagroup/geoclaw-landspill.
All contributions are welcome, including but not limited to:

* bug reports,
* bug fixes,
* documentation improvement,
* more examples or tests,
* new features, and
* performance enhancement.

Don't hesitate to ask any questions! Questions help us know what can be improved
and make this project more helpful to people.

--------------------
## How to contribute

Please open an issue at our
[GitHub repository](https://github.com/barbagroup/geoclaw-landspill) if there
are any questions, bugs, or suggestions.

Make a pull request if you want to add new features/modifications, fix bugs, or
add more examples/tests. As we try to keep the project simple, all pull requests
should make the `master` branch as the base branch. A pull request against the
`master` branch triggers Travis CI and tests defined with GitHub Actions. Please
make sure the newly added code passes all tests.

------------------------------------------------------------------------
## How to install *geoclaw-landspill* for development and run tests

In addition to the standard installation methods described in
[`deps_install_tests.md`](doc/deps_install_tests.md), developers should consider
an editable installation. With an editable installation, code modifications take
effect immediately without re-installation. Assuming currently under the
top-level folder, do

```
$ pip install --editable .
```

You may need to uninstall previously installed *geoclaw-landspill* with
`$ pip uninstall geoclaw-landspill`.

To run tests, see the last section in
[`deps_install_tests.md`](doc/deps_install_tests.md).
