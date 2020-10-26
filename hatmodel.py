#! /usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
import json
from matplotlib import pyplot as plt

import clr
# Normally I would do this down in if __name__ == "__main__", but we need the path to compartments[.exe] for the clr.AddReference call below.
parser = ArgumentParser()
# The default value here will work if the .NET assembly "compartments" is in the PYTHONPATH.
# If you are using the pycms docker container, this will be the case. Note that the default value
# doesn't have ".exe" at the end of it.
parser.add_argument("-c", "--compartments", default="bin/compartments", help="Specify full path to compartments.exe")
parser.add_argument("-p", "--png", action="store_true", help="Save output to a .png file")

args = parser.parse_args()

clr.AddReference(args.compartments)
from compartments.emodl import EmodlLoader
from compartments import Configuration as cfg
from compartments.emod.utils import SolverFactory as solvers
import cmsmodel


def main():

    # Most of this is ignored because we pass explicit values into solvers.CreateSolver() below. Really, only "prng_seed" is active.
    config = {
        "solver": "SSA",
        "runs": 11,
        "duration": 180,
        "samples": 180,
        "prng_seed": 20201025   # use this for stocasticity: datetime.now().microsecond
    }
    cfg.CurrentConfiguration = cfg.ConfigurationFromString(json.dumps(config))

    # Selectively populate a few of the species. For more fine grained control, update the code in build_model().
    model_description = build_model(**{
        "human-susceptible":10_000,
        "tsetse-susceptible":99_900,
        "tsetse-infectious":100,
        "reservoir-susceptible":1_000,
        "non-reservoir-hosts":1_000})
    model_info = load_model(model_description, cleanup=False)

    # Create an SSA solver - could just specify "SSA" or "TAU" here. Run for 3650 time units, record 3650 intermediate states of the system.
    solver = solvers.CreateSolver(config["solver"], model_info, 1, 365.0*10, 365*10)
    solver.Solve()  # Run the solver
    data = solver.GetTrajectoryData()   # Retrieve the recorded data (all observables, see build_model())
    for index, label in enumerate(solver.GetTrajectoryLabels()):
        # Each "row" of data is one trajectory of one observable, the label is observable_name{run#}
        plt.plot([float(value) for value in data[index]], label=str(label))
    plt.legend()
    if not args.png:
        plt.show()
    else:
        print("Saving plot to 'trajectory.png'")
        plt.savefig("trajectory.png")

    return


def build_model(**kwargs):

    # See hatmodel.md

    model = cmsmodel.CmsModel("hat")

    # The "odd" construction of `kwargs[...] if ... in kwargs else 0` allows you to selectively specify
    # some initial populations in the call to build_model() and those values will be used to initialize
    # the population of those species. If you do not specify a value, the initial population will be 0.
    species = [
        {"name":"human-susceptible",          "population": kwargs["human-susceptible"]          if "human-susceptible"          in kwargs else 0, "observe":True},
        {"name":"human-exposed",              "population": kwargs["human-exposed"]              if "human-exposed"              in kwargs else 0, "observe":True},
        {"name":"human-infectious-one",       "population": kwargs["human-infectious-one"]       if "human-infectious-one"       in kwargs else 0, "observe":True},
        {"name":"human-infectious-two",       "population": kwargs["human-infectious-two"]       if "human-infectious-two"       in kwargs else 0, "observe":True},
        {"name":"human-recovered",            "population": kwargs["human-recovered"]            if "human-recovered"            in kwargs else 0, "observe":True},
        {"name":"human-infection-cumulative", "population": kwargs["human-infection-cumulative"] if "human-infection-cumulative" in kwargs else 0, "observe":True},

        {"name":"tsetse-susceptible",     "population": kwargs["tsetse-susceptible"]     if "tsetse-susceptible"     in kwargs else 0, "observe":True},
        {"name":"tsetse-exposed",         "population": kwargs["tsetse-exposed"]         if "tsetse-exposed"         in kwargs else 0, "observe":True},
        {"name":"tsetse-infectious",      "population": kwargs["tsetse-infectious"]      if "tsetse-infectious"      in kwargs else 0, "observe":True},
        {"name":"tsetse-non-susceptible", "population": kwargs["tsetse-non-susceptible"] if "tsetse-non-susceptible" in kwargs else 0, "observe":True},

        # {"name":"non-reservoir-hosts", "population": kwargs["non-reservoir-hosts"] if "non-reservoir-hosts" in kwargs else 0, "observe":True},

        {"name":"reservoir-susceptible", "population": kwargs["reservoir-susceptible"] if "reservoir-susceptible" in kwargs else 0, "observe":True},
        {"name":"reservoir-exposed",     "population": kwargs["reservoir-exposed"]     if "reservoir-exposed"     in kwargs else 0, "observe":True},
        {"name":"reservoir-infectious",  "population": kwargs["reservoir-infectious"]  if "reservoir-infectious"  in kwargs else 0, "observe":True},
        {"name":"reservoir-recovered",   "population": kwargs["reservoir-recovered"]   if "reservoir-recovered"   in kwargs else 0, "observe":True}
    ]

    def _add_species(name: str, population: int, observe: bool):
        model.add_species(name, population, observe)

    for specie in species:
        _add_species(**specie)

    # https://www.medrxiv.org/content/10.1101/2020.06.23.20138065v1.full.pdf
    parameters = [
        {"name":"sigma-h",          "value":0.0833},    # incubation rate (human E->I1)
        {"name":"phi-h",            "value":0.0019},    # progression from human I1->I2
        {"name":"omega-h",          "value":0.006},     # human recovery rate
        {"name":"beta-v",           "value":0.065},     # beta for tsetse fly infection from infectious human
        {"name":"p-human-feed",     "value":0.05},      # probability of human feed
        {"name":"p-reservoir-feed", "value":0.23},      # probability of reservoir host feed (assume pigs)
        {"name":"sigma-v",          "value":0.034},     # incubation rate (tsetse E->I)
        {"name":"mu-v",             "value":0.03},      # tsetse fly mortality rate
        # _not_ from the paper referenced above
        {"name":"p-feed",           "value":1.0/3},     # probability of feeding in the first 24 hours
        {"name":"beta-h",           "value":1.0},       # beta for human infection by infectious tsetse fly
        {"name":"beta-r",           "value":1.0},       # beta for reservoir infection by infectious tsetse fly
        {"name":"phi-r",            "value":0.0019},    # reservoir incubation rate
        {"name":"omega-r",          "value":0.006},     # reservoir recovery rate
        {"name":"mu-h",             "value":1.0/80},    # human mortality rate
        {"name":"mu-r",             "value":1.0/5},     # reservoir mortality rate
    ]

    def _add_parameter(name: str, value: float):
        model.add_parameter(name, value)

    for parameter in parameters:
        _add_parameter(**parameter)

    # Convenience functions:
    model.add_function("human-population",           "(+ human-susceptible human-exposed human-infectious-one human-infectious-two human-recovered)")
    model.add_function("reservoir-population",       "(+ reservoir-susceptible reservoir-exposed reservoir-infectious reservoir-recovered)")

    # Reactions/transitions

    # human S->E->I1->I2->R
    model.add_reaction("human-infection",              ["human-susceptible"],    ["human-exposed", "human-infection-cumulative"], "(/ (* beta-h human-susceptible tsetse-infectious) human-population)")
    model.add_reaction("human-exposed-infectious",     ["human-exposed"],        ["human-infectious-one"],                        "(* sigma-h human-exposed)")
    model.add_reaction("human-infectious-progression", ["human-infectious-one"], ["human-infectious-two"],                        "(* phi-h human-infectious-one)")
    model.add_reaction("human-recovery",               ["human-infectious-two"], ["human-recovered"],                             "(* omega-h human-infectious-two)")

    # vector S->E->I & S->N (non-susceptible)
    # model.add_reaction("feed-infectious-human-infected",       ["tsetse-susceptible"], ["tsetse-exposed"],         "(* p-feed p-human-feed (/ human-infectious-one human-population) beta-v)")
    # model.add_reaction("feed-infectious-human-uninfected",     ["tsetse-susceptible"], ["tsetse-non-susceptible"], "(* p-feed p-human-feed (/ human-infectious-one human-population) (- 1 beta-v))")
    # model.add_reaction("feed-uninfectious-human",              ["tsetse-susceptible"], ["tsetse-non-susceptible"], "(* p-feed p-human-feed (- 1 (/ human-infectious-one human-population)))")
    # model.add_reaction("feed-infectious-reservoir-infected",   ["tsetse-susceptible"], ["tsetse-exposed"],         "(* p-feed p-reservoir-feed (/ reservoir-infectious reservoir-population) beta-v)")
    # model.add_reaction("feed-infectious-reservoir-uninfected", ["tsetse-susceptible"], ["tsetse-non-susceptible"], "(* p-feed p-reservoir-feed (/ reservoir-infectious reservoir-population) (- 1 beta-v))")
    # model.add_reaction("feed-uninfectious-reservoir",          ["tsetse-susceptible"], ["tsetse-non-susceptible"], "(* p-feed p-reservoir-feed (- 1 (/ reservoir-infectious reservoir-population)))")
    # model.add_reaction("feed-non-infectious-host",             ["tsetse-susceptible"], ["tsetse-non-susceptible"], "(* p-feed (- 1 (+ p-human-feed p-reservoir-feed))")
    # model.add_reaction("dont-feed",                            ["tsetse-susceptible"], ["tsetse-non-susceptible"], "(- 1 p-feed)")

    # Simplified(?) version
    model.add_function("infectious-feed", "(* p-feed (+ (* p-human-feed (/ human-infectious-one human-population)) (* p-reservoir-feed (/ reservoir-infectious reservoir-population))) beta-v)")
    model.add_reaction("feed-and-infected",      ["tsetse-susceptible"], ["tsetse-exposed"], "infectious-feed")
    model.add_reaction("become-non-susceptible", ["tsetse-susceptible"], ["tsetse-non-susceptible"], "(- 1 infectious-feed)")

    model.add_reaction("tsetse-progress-to-infectious", ["tsetse-exposed"], ["tsetse-infectious"], "(* sigma-v tsetse-exposed)")

    # reservoir S->E->I->R
    model.add_reaction("reservoir-infection",          ["reservoir-susceptible"], ["reservoir-exposed"],    "(/ (* beta-r reservoir-susceptible tsetse-infectious) reservoir-population)")
    model.add_reaction("reservoir-exposed-infectious", ["reservoir-exposed"],     ["reservoir-infectious"], "(* phi-r reservoir-exposed)")
    model.add_reaction("reservoir-recovery",           ["reservoir-infectious"],  ["reservoir-recovered"],  "(* omega-r reservoir-infectious)")

    # vital dynamics: stable population - recycle deaths directly into births (susceptible)

    # model.add_reaction("human-susceptible-death-birth",    ["human-susceptible"],   ["human-susceptible"], "(* mu-h human-susceptible)")
    model.add_reaction("human-exposed-death-birth",        ["human-exposed"],        ["human-susceptible"], "(* mu-h human-exposed)")
    model.add_reaction("human-infectious-one-death-birth", ["human-infectious-one"], ["human-susceptible"], "(* mu-h human-infectious-one)")
    model.add_reaction("human-infectious-two-death-birth", ["human-infectious-two"], ["human-susceptible"], "(* mu-h human-infectious-two)")
    model.add_reaction("human-recovered-death-birth",      ["human-recovered"],      ["human-susceptible"], "(* mu-h human-recovered)")

    # model.add_reaction("vector-susceptible-death-birth",     ["tsetse-susceptible"],     ["tsetse-susceptible"], "(* mu-h tsetse-susceptible)")
    model.add_reaction("vector-exposed-death-birth",         ["tsetse-exposed"],         ["tsetse-susceptible"], "(* mu-h tsetse-exposed)")
    model.add_reaction("vector-infectious-death-birth",      ["tsetse-infectious"],      ["tsetse-susceptible"], "(* mu-h tsetse-infectious)")
    model.add_reaction("vector-non-susceptible-death-birth", ["tsetse-non-susceptible"], ["tsetse-susceptible"], "(* mu-h tsetse-non-susceptible)")

    # model.add_reaction("reservoir-susceptible-death-birth", ["reservoir-susceptible"], ["reservoir-susceptible"], "(* mu-r reservoir-susceptible)")
    model.add_reaction("reservoir-exposed-death-birth",     ["reservoir-exposed"],     ["reservoir-susceptible"], "(* mu-r reservoir-exposed)")
    model.add_reaction("reservoir-infectious-death-birth",  ["reservoir-infectious"],  ["reservoir-susceptible"], "(* mu-r reservoir-infectious)")
    model.add_reaction("reservoir-recovered-death-birth",   ["reservoir-recovered"],   ["reservoir-susceptible"], "(* mu-r reservoir-recovered)")
 
    return model


def load_model(model, cleanup=True):

    model_info = EmodlLoader.LoadEMODLModel(str(model))

    return model_info


if __name__ == "__main__":
    main()
