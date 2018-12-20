# goutte
DigitalOcean doesn't propose any way of automating snapshots.
There are [some SaaS](https://snapshooter.io/) that can take care of it but paying to execute some API requests seemed a bit off.

That's why we developed a simple script which you can run with cron jobs or in CI services like Travis for free.

## TODO
- [x] Configuration from a single TOML file
- [x] Droplets snapshots
- [x] Droplets snapshots pruning
- [x] Volume snapshots
- [x] Volume snapshots pruning
- [ ] Slack alerting
- [ ] Add droplets and volumes by tag

## Requirements
- Python ^3.6
- A DigitalOcean account

## Installation
Install it directly from pip:
```bash
pip3 install --user goutte
```

## Configuration file
Goutte takes its configuration from a pretty straightforward toml file.
We provided and example in `goutte.example.toml`.

```toml
retention = 10     # Number of backups to keep per droplet/volume

[droplets]
names = [          # Array of droplets you want to snapshot
  'server01',
  'server02',
  'server03',
]

[volumes]
names = [          # Array of volumes you want to snapshot
  'db01',
  'redis01',
  'redis02',
]
```

## Usage
Goutte takes two arguments which can also be set via environment variables:

| # | Help     | Description                         | Environment variable |
| - | -------- | ----------------------------------- | -------------------- |
| 1 | CONFIG   | Path to the toml configuration file | `GOUTTE_CONFIG`      |
| 2 | DO_TOKEN | Your DigitalOcean API token         | `GOUTTE_DO_TOKEN`    |

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
$ goutte goutte.toml $do_token --only snapshot
13:32:48 - INFO - Starting goutte v1.0.0
13:32:52 - INFO - sgp1-website-01 - Snapshot (goutte-sgp1-website-01-20181220-56bde)
13:32:59 - INFO - sgp1-mariadb-01 - Snapshot (goutte-sgp1-mariadb-01-20181220-3673d)
```

## Run with Docker
We have a Docker image ready for you to use on Docker Hub.
It will read by default the configuration under `/goutte/goutte.toml`

```bash
docker run \
  -e GOUTTE_DO_TOKEN=${do_token} \
  -v $(pwd)/goutte.toml:/goutte/goutte.toml \
  tomochain:goutte
```

## Automating
You can easily automate it via cron job or by leveraging free CI tools like Travis.
We provided and example travis configuration in `travis.example.yml`.

You just need to set the environment variables on the Travis website and schedule it with the frequency of your backups.

TODO
