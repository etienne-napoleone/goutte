def nothing(*args, **kwargs):
    pass


class Snapshot:
    def __init__(self, created_at=None, name=None, id=None):
        self.created_at = created_at
        self.name = name
        self.id = id

    def destroy(self):
        pass

    @staticmethod
    def get_object(api_token=None, snapshot_id=None):
        if snapshot_id == '1337':
            return Snapshot(name=f'snapshot{snapshot_id}', id=snapshot_id,
                            created_at=f'{snapshot_id}')
        else:
            return Snapshot(name=f'goutte-snapshot{snapshot_id}',
                            id=snapshot_id, created_at=f'{snapshot_id}')


class Volume:
    def __init__(self, name=None, snapshots=None, throw=None):
        self.name = name
        self.snapshots = snapshots
        self.throw = throw

    def get_snapshots(self):
        return self.snapshots

    def snapshot(self, name):
        pass


class Droplet:
    def __init__(self, name=None, snapshot_ids=None):
        self.name = name
        self.snapshot_ids = snapshot_ids

    def take_snapshot(self, name):
        pass


class Manager:
    def __init__(self, token=None):
        self.token = token

    def get_all_volumes(self):
        return [
            Volume(name='testvol')
        ]

    def get_all_droplets(self):
        return [
            Droplet(name='testdroplet')
        ]
