# goutte <a href="https://travis-ci.org/tomochain/goutte"><img align="right" src="https://travis-ci.org/tomochain/goutte.svg?branch=develop"></a>
DigitalOcean doesn't propose any way of automating snapshots.
There are [some SaaS](https://snapshooter.io/) that can take care of it but paying to execute some API requests seemed a bit off.

That's why we developed a simple script which can run with cron jobs or in CI services like Travis for free.
We use it daily to manage [our backups](https://github.com/tomochain/backups).

It includes:
- Snapshoting droplets
- Snapshoting volumes
- Retention policy
- Pruning snapshots

## Requirements
- Python ^3.6
- A DigitalOcean account

## Installation
Install it directly from pip:
```bash
pip3 install --user goutte
```

## Configuration file
Goutte takes its configuration from a pretty straightforward yml file.
We provided and example in `goutte.example.yml`.

```yml
name: weekly
keep: 5
targets:
  droplets:
    names:
      - server01
      - server02
    tags:
      - prod
  volumes:
    names:
      - vol01
      - vol02
```

## Usage
Goutte takes two arguments which can also be set via environment variables:

| # | Help     | Description                        | Environment variable |
|---|----------|------------------------------------|----------------------|
| 1 | CONFIG   | Path to the yml configuration file | `GOUTTE_CONFIG`      |
| 2 | DO_TOKEN | Your DigitalOcean API token        | `GOUTTE_DO_TOKEN`    |

```bash
Usage: goutte [OPTIONS] CONFIG DO_TOKEN

  DigitalOcean snapshots automation.

Options:
  --only [snapshot|prune]  Only snapshot or only prune
  --debug                  Enable debug logging
  --version                Show the version and exit.
  --help                   Show this message and exit.
```

Running "snapshot only" for a configuration file containing one droplet and one volume:
```bash
$ goutte goutte.yml $do_token --only snapshot
13:32:48 - INFO - Starting goutte v1.0.1
13:32:52 - INFO - sgp1-website-01 - Snapshot (goutte-sgp1-website-01-20181220-56bde)
13:32:59 - INFO - sgp1-mariadb-01 - Snapshot (goutte-sgp1-mariadb-01-20181220-3673d)
```

## Run with Docker
We have a Docker image ready for you to use on Docker Hub.
It will read by default the configuration under `/app/goutte.yml`

```bash
docker run \
  -e GOUTTE_DO_TOKEN=${do_token} \
  -v $(pwd)/goutte.yml:/app/goutte.yml \
  tomochain/goutte
```

## Automating with Travis
You can easily automate it via cron job but the easiest way would be by leveraging free CI tools like Travis.

1. You can create a repo which contains your `goutte.yml` configuration and the following travis file `.travis.yml` :

```yml
language: python
python: 3.6

install:
  - pip install goutte

script:
  - goutte goutte.yml # Don't forget to set GOUTTE_DO_TOKEN in Travis config
```

2. Enable the repo in Travis and then go to the configuration
3. Add the environment variable GOUTTE_DO_TOKEN with the value of your DigitalOcean API key
4. Enable daily cron job
5. You're good to go, goutte will run everyday and take care of the snapshots.

**Note**: You can have different retentions for different volumes by having multiple configurations.
```yml
# ...
script:
  - goutte 10days.yml
  - goutte 1day.yml
```

You can see how we set it up for ourself [here](https://github.com/tomochain/backups).
