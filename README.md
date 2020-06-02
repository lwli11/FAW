This README documents the Galois Format Analysis Workbench (GFAW) for developers
creating their own distributions of the workbench. The core workbench source
should remain unchanged, but distribution creators are encouraged to develop
their own plugins to support new file formats or enhance support for existing
formats.

To create a new distribution, create a new subfolder, modeled off of the `pdf`
base distribution. Available options are documented in `config.json5` within
that folder.

Please do not add files directly to this folder.

To get started, run:

    pip3 install -r requirements.txt
    python3 workbench.py pdf /path/to/pdf/folder

Then point your browser at http://localhost:8123

While developing a distribution, consider using `--development` to use Vue's
live reload functionality and to mount the distribution's folder into
`/home/` in a way which allows for making changes without stopping and starting
the development server.

To build a standalone workbench in `build/label`, run:

    python3 workbench.py pdf build/label

See README-dist.md for additional information on running the workbench docker
image in a standalone fashion.

