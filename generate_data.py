from titan.model import TITAN
from titan.parse_params import create_params
import titan.population_io as pio
import titan.output as ao

import os
import sys

param_file = "viz_basic.yml"
setting = "scott"
outdir="results"

try:
    os.mkdir(outdir)
except:
    print("results directory already exists, exiting")
    exit()

params = create_params(setting, param_file, outdir)

model = TITAN(params)

def run(self, outdir: str):
        """
        Runs the model for the number of time steps defined in params, at each time step does:

        1. Increments time
        2. Takes one step
        3. Resets trackers
        4. Saves population for visualization

        args:
            outdir: path to directory where results should be saved
        """
        # make sure initial state of things get printed
        stats = ao.get_stats(
            self.pop.all_agents,
            self.deaths,
            self.params,
            self.exposures,
            self.features,
            self.time,
        )
        self.print_stats(stats, outdir)

        if self.params.model.time.burn_steps > 0:
            print("\t===! Start Burn Loop !===")

        # time starts at negative burn steps, model run starts at t = 1
        while self.time < self.params.model.time.num_steps:
            if self.time == 0:
                if self.params.model.time.burn_steps > 0:
                    print("\t===! Burn Loop Complete !===")
                print("\t===! Start Main Loop !===")

            self.time += 1
            self.step(outdir)
            self.reset_trackers()

            # save population for viz
            pop_outdir = os.path.join(outdir, str(self.time))
            os.mkdir(pop_outdir)
            pio.write(self.pop, pop_outdir, compress=False)

        print("\t===! Main Loop Complete !===")

run(model, outdir)
