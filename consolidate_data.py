import csv
import os
import glob
import re

def read_timestep(root_path: str, time: str):
    """
    Read a population from file and return a list of dictionaries of the relationships and the agents

    args:
        path: the directory containing all the timestep foldrs
        timestep: which timestep (folder) to read
    returns:
        the re-constituted population
    """
    path = os.path.join(root_path, time)

    agent_file = glob.glob(os.path.join(path, "*_agents.csv"))[0]
    rel_file = glob.glob(os.path.join(path, "*_relationships.csv"))[0]
    feat_files = glob.glob(os.path.join(path, "*_feat_*.csv"))
    exposure_files = glob.glob(os.path.join(path, "*_exposure_*.csv"))
    assert os.path.isfile(agent_file), f"can't find agents.csv in {dir}"
    assert os.path.isfile(rel_file), f"can't find relationships.csv in {dir}"

    _, agent_filename = os.path.split(agent_file)

    # create agents dict
    agents = {}

    # re-create all agents and add to population
    with open(agent_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            agents[row["id"]] = row
            agents[row["id"]]["time"] = time

    def update_agent_extras(files, extra_type):
        pattern = re.compile(f"^.*_{extra_type}_(.*)\.csv$")
        for file in files:
            m = pattern.match(file)
            if m is not None:
                extra = m.group(1)
                with open(file, newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        for k, v in row.items():
                            if k != "agent":
                                agents[row["agent"]][f"{extra}_{k}"] = v

    update_agent_extras(feat_files, "feat")
    update_agent_extras(exposure_files, "exposure")

    # re-create all relationships and write to file
    rels = []
    with open(rel_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["time"] = time
            rels.append(row)

    return rels, list(agents.values())


agent_dicts = []
rel_dicts = []
resultdir = "results"

for path in os.listdir(resultdir):
    if os.path.isdir(os.path.join(resultdir, path)):
        rels, agents = read_timestep(resultdir, path)
        rel_dicts.extend(rels)
        agent_dicts.extend(agents)

print(f"Creating rel file")
with open("rels.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rel_dicts[1].keys()))
    writer.writeheader()
    for item in rel_dicts:
        writer.writerow(item)

print(f"Creating agent file")
with open("agents.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(agent_dicts[1].keys()))
    writer.writeheader()
    for item in agent_dicts:
        writer.writerow(item)
