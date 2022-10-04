# WJS - JCOM profile

**Experimental**

A django app for Janeway that enriches the `Account` profile with the
field "profession".

**Important**: needs JCOM graphical theme (because of some modified templates)

The branches `as-plugin` and `simpler-name` have this app in the form
of a Janeway's plugin, but I've abandoned them because of difficulties
in test "finding" (ala `manage.py test plugins.myplugin`) and because
I don't need to be able to enable/disable the plugin TTW.

## Install & use

This is a django app that should live inside Janeway. To use it, proceed as follows:

1. Activate your Janeway's virtual environment and install in development mode:
   `pip install -e .../wjs-profile-project`

2. Migrations should be run specifying the sub-package name:
   `./manage.py migrate jcom_profile`

### pre-commit

This project uses [pre-commit](https://pre-commit.com/) hooks to enforce code style and linting.

When you make a commit, it will trigger `pre-commit` hooks which will check staged files style
on `.pre-commit-config.yaml` rules basis.
1. Install `pre-commit`:
   ```shell
   pip install pre-commit
   ```
2. Install `pre-commit` hooks script in repository root:
   ```shell
   pre-commit install
   ```

3. If you want to update `pre-commit` dependencies, run the following command:
   ```shell
   pre-commit autoupdate
   ```

### TODO: (aka "not yet implemented"...)

1. Activate your Janeway's virtual environment and install the package
   of this app (please see
   https://gitlab.sissamedialab.it/ml-foss/omlpi/-/packages)

2. Add "wjs\_profession" to Janeway's INSTALLED\_APPS in
   `src/core/janeway\_global\_setting.py` like this::
   ```
   INSTALLED_APPS = [
       ...
       'wjs_profession',
   ]
   ```

See https://gitlab.sissamedialab.it/medialab/janeway/-/issues/7
