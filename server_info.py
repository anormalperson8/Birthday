import json
import os
from dotenv import load_dotenv

path = os.path.dirname(os.path.abspath(__file__))
data_path = f"{path}/data/"


class Server:
    def __init__(self, server_id: int, announcement_channel: int, moderator_roles: list,
                 allowed_channels: list, role_to_ping: int):
        self.serverID = server_id
        self.announcementChannel = announcement_channel
        self.moderatorRoles = moderator_roles
        self.allowedChannels = allowed_channels
        self.role_to_ping = role_to_ping


# Returns a list of Server objects
def get_servers():
    f = open(data_path + "/server.json", 'r')
    data = json.load(f)
    servers = []
    for server in data["server"]:
        servers.append(Server(server["id"], server["announcementChannel"],
                              server["moderatorRoles"], server["allowedChannels"],
                              server["RoleToPing"]))
    return servers


# Returns the index of the server in the list of servers
def search_for_server_id(servers: list, server_id: int):
    return [i for i in range(len(servers)) if servers[i].serverID == server_id][0]


# Returns the server object in the list of servers
def search_for_server(servers: list, server_id: int):
    return [i for i in servers if i.serverID == server_id][0]




