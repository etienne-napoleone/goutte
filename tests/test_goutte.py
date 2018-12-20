from goutte import __version__
from goutte import main
from tests import mock


def test_version():
    assert __version__ == '1.0.0'


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
