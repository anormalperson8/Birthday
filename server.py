import json
import os
from dotenv import load_dotenv

path = os.path.dirname(os.path.abspath(__file__))
data_path = f"{path}/data/"
load_dotenv(f"{data_path}data.env")


class Server:
    def __init__(self, server_id: int, announcement_channel: int, moderator_roles: list,
                 allowed_channels: list, role_to_ping: int):
        self.server_id = server_id
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
