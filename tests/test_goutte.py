from click.testing import CliRunner
import digitalocean
import pytest
import toml

from goutte import __version__
from goutte import main
from tests import mock


def test_version():
    assert __version__ == '1.0.0'


def test_entrypoint(caplog, monkeypatch):
    def load_config(*args):
        return {'retention': 2}
    monkeypatch.setattr(main, '_load_config', load_config)
    monkeypatch.setattr(main, '_process_droplets', mock.nothing)
    monkeypatch.setattr(main, '_process_volumes', mock.nothing)
    runner = CliRunner()
    with runner.isolated_filesystem():
        with caplog.at_level('INFO'):
            with open('test.toml', 'w') as f:
                f.write('Hello World!')
            result = runner.invoke(main.entrypoint, [
                'test.toml',
                'token123',
            ])
            assert result.exit_code == 0
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'INFO'


def test_entrypoint_debug(caplog, monkeypatch):
    def load_config(*args):
        return {'retention': 2}
    monkeypatch.setattr(main, '_load_config', load_config)
    monkeypatch.setattr(main, '_process_droplets', mock.nothing)
    monkeypatch.setattr(main, '_process_volumes', mock.nothing)
    monkeypatch.setattr(main.log, 'setLevel', mock.nothing)
    runner = CliRunner()
    with runner.isolated_filesystem():
        with caplog.at_level('INFO'):
            with open('test.toml', 'w') as f:
                f.write('Hello World!')
            result = runner.invoke(main.entrypoint, [
                'test.toml',
                'token123',
                '--debug',
            ])
            assert result.exit_code == 0
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'INFO'


def test_entrypoint_only(caplog, monkeypatch):
    def load_config(*args):
        return {'retention': 2}
    monkeypatch.setattr(main, '_load_config', load_config)
    monkeypatch.setattr(main, '_process_droplets', mock.nothing)
    monkeypatch.setattr(main, '_process_volumes', mock.nothing)
    monkeypatch.setattr(main.log, 'setLevel', mock.nothing)
    runner = CliRunner()
    with runner.isolated_filesystem():
        with caplog.at_level('INFO'):
            with open('test.toml', 'w') as f:
                f.write('Hello World!')
            result = runner.invoke(main.entrypoint, [
                'test.toml',
                'token123',
                '--debug',
                '--only', 'prune',
            ])
            assert result.exit_code == 0
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'INFO'


def test_load_config(monkeypatch):
    def load(file):
        return {'retention': 2}
    monkeypatch.setattr(toml, 'load', load)
    assert main._load_config(mock.File(name='test.toml'))['retention'] == 2


def test_load_config_raise_typeerror(caplog, monkeypatch):
    def load(file):
        raise TypeError
    monkeypatch.setattr(toml, 'load', load)
    with caplog.at_level('INFO'):
        with pytest.raises(SystemExit) as e:
            main._load_config(mock.File(name='test.toml'))
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'CRITICAL'
            assert e.type == SystemExit
            assert e.value.code == 1


def test_load_config_raise_tomldecodeerror(caplog, monkeypatch):
    def load(file):
        raise toml.TomlDecodeError
    monkeypatch.setattr(toml, 'load', load)
    with caplog.at_level('INFO'):
        with pytest.raises(SystemExit) as e:
            main._load_config(mock.File(name='test.toml'))
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'CRITICAL'
            assert e.type == SystemExit
            assert e.value.code == 1


def test_load_config_config_keyerror(caplog, monkeypatch):
    def load(file):
        return {}
    monkeypatch.setattr(toml, 'load', load)
    with caplog.at_level('INFO'):
        with pytest.raises(SystemExit) as e:
            main._load_config(mock.File(name='test.toml'))
            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'CRITICAL'
            assert e.type == SystemExit
            assert e.value.code == 1


def test_process_droplets(caplog, monkeypatch):
    def get_droplets(names):
        return [mock.Droplet(name='testdroplet')]
    conf = {'retention': 1, 'droplets': {'names': ['testdroplet']}}
    monkeypatch.setattr(main, '_get_droplets', get_droplets)
    monkeypatch.setattr(main, '_prune_droplet_snapshots', mock.nothing)
    monkeypatch.setattr(main, '_snapshot_droplet', mock.nothing)
    with caplog.at_level('INFO'):
        main._process_droplets(conf=conf, only=None)
        assert len(caplog.records) == 0


def test_process_droplets_no_vol(caplog, monkeypatch):
    def get_droplets(names):
        return []
    conf = {'retention': 1, 'droplets': {'names': ['testdroplet']}}
    monkeypatch.setattr(main, '_get_droplets', get_droplets)
    monkeypatch.setattr(main, '_prune_droplet_snapshots', mock.nothing)
    monkeypatch.setattr(main, '_snapshot_droplet', mock.nothing)
    with caplog.at_level('INFO'):
        main._process_droplets(conf=conf, only=None)
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'WARNING'


def test_process_droplets_key_error(caplog, monkeypatch):
    def get_droplets(names):
        return [mock.Droplet(name='testdroplet')]
    conf = {'retention': 1, 'droplets': {'names': ['testdroplet2']}}
    monkeypatch.setattr(main, '_get_droplets', get_droplets)
    monkeypatch.setattr(main, '_prune_droplet_snapshots', mock.nothing)
    monkeypatch.setattr(main, '_snapshot_droplet', mock.nothing)
    with caplog.at_level('INFO'):
        main._process_droplets(conf=conf, only=None)
        assert len(caplog.records) == 0


def test_process_volumes(caplog, monkeypatch):
    def get_volumes(names):
        return [mock.Volume(name='testvol')]
    conf = {'retention': 1, 'volumes': {'names': ['testvol']}}
    monkeypatch.setattr(main, '_get_volumes', get_volumes)
    monkeypatch.setattr(main, '_prune_volume_snapshots', mock.nothing)
    monkeypatch.setattr(main, '_snapshot_volume', mock.nothing)
    with caplog.at_level('INFO'):
        main._process_volumes(conf=conf, only=None)
        assert len(caplog.records) == 0


def test_process_volumes_no_vol(caplog, monkeypatch):
    def get_volumes(names):
        return []
    conf = {'retention': 1, 'volumes': {'names': ['testvol']}}
    monkeypatch.setattr(main, '_get_volumes', get_volumes)
    monkeypatch.setattr(main, '_prune_volume_snapshots', mock.nothing)
    monkeypatch.setattr(main, '_snapshot_volume', mock.nothing)
    with caplog.at_level('INFO'):
        main._process_volumes(conf=conf, only=None)
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'WARNING'


def test_process_volumes_key_error(caplog, monkeypatch):
    def get_volumes(names):
        return [mock.Volume(name='testvol')]
    conf = {'retention': 1, 'volumes': {'names': ['testvol2']}}
    monkeypatch.setattr(main, '_get_volumes', get_volumes)
    monkeypatch.setattr(main, '_prune_volume_snapshots', mock.nothing)
    monkeypatch.setattr(main, '_snapshot_volume', mock.nothing)
    with caplog.at_level('INFO'):
        main._process_volumes(conf=conf, only=None)
        assert len(caplog.records) == 0


def test_get_droplets(monkeypatch):
    monkeypatch.setattr(digitalocean, 'Manager', mock.Manager)
    assert 'testdroplet' in main._get_droplets(['testdroplet'])[0].name


def test_snapshot_droplet(caplog):
    droplet = mock.Droplet(name='testdroplet')
    with caplog.at_level('INFO'):
        main._snapshot_droplet(droplet)
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'INFO'
        assert 'testdroplet' in caplog.records[0].message


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


def test_get_volumes(monkeypatch):
    monkeypatch.setattr(digitalocean, 'Manager', mock.Manager)
    assert 'testvol' in main._get_volumes(['testvol'])[0].name


def test_snapshot_volume(caplog):
    volume = mock.Volume('testvol')
    with caplog.at_level('INFO'):
        main._snapshot_volume(volume)
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'INFO'
        assert 'testvol' in caplog.records[0].message


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
