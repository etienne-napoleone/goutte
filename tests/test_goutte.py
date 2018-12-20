import digitalocean

from goutte import __version__
from goutte import main
from tests import mock


def test_version():
    assert __version__ == '1.0.0'


def test_prune_droplet_snapshots(caplog, monkeypatch):
    monkeypatch.setattr(digitalocean, 'Snapshot', mock.Snapshot)
    droplet = mock.Droplet(name='testdroplet', snapshot_ids=['3', '2', '1'])
    with caplog.at_level('INFO'):
        main._prune_droplet_snapshots(droplet, 1)
        assert len(caplog.records) == 2
        for record in caplog.records:
            assert record.levelname == 'INFO'
            assert "goutte-snapshot3" not in record.message


def test_prune_droplet_snapshots_goutte_prefix_only(caplog, monkeypatch):
    monkeypatch.setattr(digitalocean, 'Snapshot', mock.Snapshot)
    droplet = mock.Droplet(name='testdroplet', snapshot_ids=['1337', '2', '1'])
    with caplog.at_level('INFO'):
        main._prune_droplet_snapshots(droplet, 1)
        assert len(caplog.records) == 1
        for record in caplog.records:
            assert record.levelname == 'INFO'
            assert "snapshot1337" not in record.message
            assert "goutte-snapshot2" not in record.message


def test_get_volumes(caplog):
    exceptions = [
        digitalocean.baseapi.TokenError,
        digitalocean.baseapi.DataReadError,
        digitalocean.baseapi.JSONReadError,
        digitalocean.baseapi.NotFoundError,
        Exception,
    ]
    for exception in exceptions:
        volume = mock.Volume(name='testvol', throw=exception)
        with caplog.at_level('INFO'):
            main._snapshot_volume(volume)
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'ERROR'
            caplog.clear()


def test_snapshot_volume(caplog):
    volume = mock.Volume('testvol')
    with caplog.at_level('INFO'):
        main._snapshot_volume(volume)
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'INFO'
        assert 'testvol' in caplog.records[0].message


def test_snapshot_volume_raise(caplog):
    exceptions = [
        digitalocean.baseapi.TokenError,
        digitalocean.baseapi.DataReadError,
        digitalocean.baseapi.JSONReadError,
        digitalocean.baseapi.NotFoundError,
        Exception,
    ]
    for exception in exceptions:
        volume = mock.Volume(name='testvol', throw=exception)
        with caplog.at_level('INFO'):
            main._snapshot_volume(volume)
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'ERROR'
            caplog.clear()


def test_prune_volume_snapshots(caplog):
    volume = mock.Volume('testvol', [
        mock.Snapshot(name='goutte-snapshot1', created_at='2018'),
        mock.Snapshot(name='goutte-snapshot2', created_at='2017'),
        mock.Snapshot(name='goutte-snapshot3', created_at='2016'),
    ])
    with caplog.at_level('INFO'):
        main._prune_volume_snapshots(volume, 1)
        assert len(caplog.records) == 2
        for record in caplog.records:
            assert record.levelname == 'INFO'
            assert "goutte-snapshot1" not in record.message


def test_prune_volume_snapshots_goutte_prefix_only(caplog):
    volume = mock.Volume('testvol', [
        mock.Snapshot(name='snapshot1', created_at='2018'),
        mock.Snapshot(name='snapshot2', created_at='2017'),
    ])
    with caplog.at_level('INFO'):
        main._prune_volume_snapshots(volume, 1)
        assert len(caplog.records) == 0


def test_prune_volume_snapshots_raise(caplog):
    exceptions = [
        digitalocean.baseapi.TokenError,
        digitalocean.baseapi.DataReadError,
        digitalocean.baseapi.JSONReadError,
        digitalocean.baseapi.NotFoundError,
        Exception,
    ]
    for exception in exceptions:
        volume = mock.Volume(name='testvol', throw=exception)
        with caplog.at_level('INFO'):
            main._prune_volume_snapshots(volume, 1)
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'ERROR'
            caplog.clear()


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
