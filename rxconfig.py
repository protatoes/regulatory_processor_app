"""
Reflex configuration for the regulatory_processor project.

This file tells the Reflex CLI which Python module contains the
application definition.  The ``app_name`` must match the name of
the package where ``app`` is defined (in this case
``regulatory_processor``)【338122900162100†L69-L96】.  See the official
documentation for details.
"""

import reflex as rx  # type: ignore

# The name of the Reflex app package.  When running ``reflex run``
# the CLI will import ``regulatory_processor/app.py`` and look for
# an ``app`` instance.
config = rx.Config(
    app_name="regulatory_processor",
    # Disable the sitemap plugin to suppress runtime warnings.  This
    # plugin generates a sitemap.xml file during build; we are not
    # using it in this application, so disabling it avoids the
    # warnings shown by the CLI during startup.
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)