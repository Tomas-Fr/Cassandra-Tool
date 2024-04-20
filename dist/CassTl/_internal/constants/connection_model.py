from cassandra.cluster import Cluster


class Connection(dict):
    def __init__(self: 'Connection', cluster: Cluster, connection_profile_name: str) -> None:
        self.cluster = cluster
        self.connection_profile_name = connection_profile_name