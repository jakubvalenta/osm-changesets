# OpenStreetMap Changesets

A website that shows changesets by an OpenStreetMap user including map images
and an RSS/Atom feed.

You can find the app at [osm-changesets.ooooo.page](https://osm-changesets.ooooo.page).

## Installation

### Mac

```shell
$ brew install poetry
$ make setup
```

### Arch Linux

```shell
# pacman -S python-poetry
$ make setup
```

### Other systems

Install these dependencies manually:

- Python >= 3.11
- poetry

Then run:

```shell
$ make setup
```

## Usage

1. Migrate the database:

    ```shell
    $ make migrate
    ```

2. Start the Redis message broker:

    ```shell
    $ make redis
    ```

3. Start the Celery worker:

    ```shell
    $ make worker
    ```

4. Start the development server

    ```shell
    $ make run
    ```

## Development

### Installation

```shell
$ make setup
```

### Testing and linting

```shell
$ make test
$ make lint
```

### Help

```shell
$ make help
```

## Contributing

__Feel free to remix this project__ under the terms of the GNU General Public
License version 3 or later. See [COPYING](./COPYING) and [NOTICE](./NOTICE).
