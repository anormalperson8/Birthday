import json
import os

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
    f = open(data_path + "server.json", 'r')
    data = json.load(f)
    servers = []
    for server in data["server"]:
        servers.append(Server(server["id"], server["announcementChannel"],
                              server["moderatorRoles"], server["allowedChannels"],
                              server["RoleToPing"]))
    f.close()
    return servers


# Returns the index of the server in the list of servers
def search_for_server_id(servers: list, server_id: int):
    return [i for i in range(len(servers)) if servers[i].serverID == server_id][0]


# Returns the server object in the list of servers
def search_for_server(servers: list, server_id: int):
    return [i for i in servers if i.serverID == server_id][0]


def write(servers: list[Server]):
    w = open(data_path + "server2.json", 'w')
    objs = []
    for server in servers:
        s = {
            "id": server.serverID,
            "announcementChannel": server.announcementChannel,
            "moderatorRoles": server.moderatorRoles,
            "allowedChannels": server.allowedChannels,
            "RoleToPing": server.role_to_ping
            }
        objs.append(s)
    obj = {"server": objs}
    w.write(json.dumps(obj, indent=2))
    w.close()
    os.remove(data_path + "server.json")
    os.rename(data_path + "server2.json", data_path + "server.json")


# Edits server info
def modify(server_id: int, stat: bool, announcement_channel: int = None, moderator_role: int = None,
           allowed_channel: int = None, role_to_ping: int = None):
    servers = get_servers()
    done = False
    message = "Problem: Server was not found."
    for server in servers:
        if server.serverID == server_id:
            if announcement_channel is not None:
                if stat:
                    if announcement_channel != server.announcementChannel:
                        server.announcementChannel = announcement_channel
                        done = True
                        message = f"Announcement channel is set to channel with id {announcement_channel}."
                    else:
                        message = f"Problem: This is already the announcement channel!"
                else:
                    server.announcementChannel = 1
                    done = True
                    message = f"Announcement channel is removed."
                break

            if moderator_role is not None:
                if stat and moderator_role not in server.moderatorRoles:
                    server.moderatorRoles.append(moderator_role)
                    done = True
                    message = f"Role with id {moderator_role} is added to the list of permitted roles."
                elif stat:
                    message = (f"Problem: Role with id {moderator_role} could not be added to the list of "
                               f"permitted roles.")
                elif not stat and moderator_role in server.moderatorRoles:
                    server.moderatorRoles.remove(moderator_role)
                    done = True
                    message = f"Role with id {moderator_role} is removed from the list of permitted roles."
                elif not stat:
                    message = (f"Problem: Role with id {moderator_role} could not be removed from the list of "
                               f"permitted roles.")
                break

            if allowed_channel is not None:
                if stat and allowed_channel not in server.allowedChannels:
                    server.allowedChannels.append(allowed_channel)
                    done = True
                    message = f"Channel with id {allowed_channel} is added to the list of permitted channels."
                elif stat:
                    message = (f"Problem: Channel with id {allowed_channel} could not be added to the list of "
                               f"permitted channels.")
                elif not stat and allowed_channel in server.allowedChannels:
                    server.allowedChannels.remove(allowed_channel)
                    done = True
                    message = f"Channel with id {allowed_channel} is removed from the list of permitted channels."
                elif not stat:
                    message = (f"Problem: Channel with id {allowed_channel} could not be removed from the list of "
                               f"permitted channels.")
                break

            if role_to_ping is not None:
                if stat:
                    if role_to_ping != server.role_to_ping:
                        server.role_to_ping = role_to_ping
                        done = True
                        message = f"Role to ping is set to role with id {role_to_ping}."
                    else:
                        message = f"Problem: This is already the role to ping!."
                else:
                    server.role_to_ping = 1
                    done = True
                    message = f"Role to ping is removed."
                break

    write(servers)
    return done, message

