class Snapshot:
    def __init__(self, created_at=None, name=None):
        self.created_at = created_at
        self.name = name

    def destroy(self):
        print(self.name)


class Volume:
    def __init__(self, name=None, snapshots=None, throw=None):
        self.name = name
        self.snapshots = snapshots
        self.throw = throw

    def get_snapshots(self):
        if self.throw:
            raise self.throw
        return self.snapshots
