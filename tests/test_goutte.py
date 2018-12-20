import digitalocean

from goutte import __version__
from goutte import main
from tests import mock


def test_version():
    assert __version__ == '1.0.0'


def test_prune_droplet_snapshots(capsys):
    volume = mock.Volume('testvol', [
        mock.Snapshot(name='goutte-snapshot1', created_at='2018'),
        mock.Snapshot(name='goutte-snapshot2', created_at='2017'),
        mock.Snapshot(name='goutte-snapshot3', created_at='2016'),
    ])
    main._prune_volume_snapshots(volume, 1)
    deleted = capsys.readouterr()
    assert "goutte-snapshot1" not in deleted.out
    assert "goutte-snapshot2" in deleted.out
    assert "goutte-snapshot3" in deleted.out


def test_prune_droplet_snapshots_goutte_prefix_only(capsys):
    volume = mock.Volume('testvol', [
        mock.Snapshot(name='snapshot1', created_at='2018'),
        mock.Snapshot(name='snapshot2', created_at='2017'),
    ])
    main._prune_volume_snapshots(volume, 1)
    deleted = capsys.readouterr()
    assert "snapshot1" not in deleted.out
    assert "snapshot2" not in deleted.out


def test_prune_droplet_snapshots_goutte_raise(caplog):
    exceptions = [
        digitalocean.baseapi.TokenError,
        digitalocean.baseapi.DataReadError,
        digitalocean.baseapi.JSONReadError,
        digitalocean.baseapi.NotFoundError
    ]
    for exception in exceptions:
        volume = mock.Volume(name='testvol', throw=exception)
        with caplog.at_level('ERROR'):
            main._prune_volume_snapshots(volume, 1)


def test_order_snapshots():
    snapshots = [
        mock.Snapshot(created_at='2014-01-26T11:20:14Z'),
        mock.Snapshot(created_at='2018-12-26T16:41:44Z'),
        mock.Snapshot(created_at='2018-12-26T16:40:98Z'),
    ]
    ordered_snapshots = main._order_snapshots(snapshots)
    assert ordered_snapshots[0].created_at == '2014-01-26T11:20:14Z'
    assert ordered_snapshots[1].created_at == '2018-12-26T16:40:98Z'
    assert ordered_snapshots[2].created_at == '2018-12-26T16:41:44Z'
