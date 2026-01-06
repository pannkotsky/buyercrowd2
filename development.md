# Buyercrowd - Development

## Docker Compose

- Copy `.env.example` file at the root of a project to `.env`, make necessary changes if needed.

- Start the local stack with Docker Compose:

```bash
make dev
```

- Start the backend and frontend services locally as described in [back/README.md](./back/README.md) and [front/README.md](./front/README.md).

- Now you can open your browser and interact with these URLs:

Frontend: <http://localhost>

GraphiQL: <http://localhost/api/v1/graphql>

Automatic interactive documentation for REST API with Swagger UI: <http://localhost/docs>

## Mailcatcher

Mailcatcher is a simple SMTP server that catches all emails sent by the backend during local development. Instead of sending real emails, they are captured and displayed in a web interface.

This is useful for:

- Testing email functionality during development
- Verifying email content and formatting
- Debugging email-related functionality without sending real emails

The backend is automatically configured to use Mailcatcher when running with Docker Compose locally (SMTP on port 1025). All captured emails can be viewed at <http://localhost:1080>.

## Docker Compose files and env vars

There is a base `docker-compose-base.yml` file with common services, like db.

And there's also a `docker-compose-local.yml` with overrides and additions for development.

For production-like use there is a `docker-compose-prod.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

For convenience there are commands in `Makefile` to run dev and prod stacks.

## Pre-commits and code linting

we are using a tool called [prek](https://prek.j178.dev/) (modern alternative to [Pre-commit](https://pre-commit.com/)) for code linting and formatting.

When you install it, it runs right before making a commit in git. This way it ensures that the code is consistent and formatted even before it is committed.

You can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

#### Install prek to run automatically

`prek` is already part of the dependencies of the project.

After having the `prek` tool installed and available, you need to "install" it in the local repository, so that it runs automatically before each commit.

Using `uv`, you could do it with (make sure you are inside `back` folder):

```bash
❯ uv run prek install -f
prek installed at `../.git/hooks/pre-commit`
```

The `-f` flag forces the installation, in case there was already a `pre-commit` hook previously installed.

Now whenever you try to commit, e.g. with:

```bash
git commit
```

...prek will run and check and format the code you are about to commit, and will ask you to add that code (stage it) with git again before committing.

Then you can `git add` the modified/fixed files again and now you can commit.

#### Running prek hooks manually

you can also run `prek` manually on all the files, you can do it using `uv` with:

```bash
uv run prek run --all-files
```
