# Project 1-pager:  Developing a python-based compartmental model framework for epidemiological modeling

The primary aim of this project is to construct a python-based modeling framework that builds and simulates discrete stochastic compartmental models.  This tool would enable researchers to quickly and efficiently spin up bespoke compartmental models and simulate them accurately and efficiently.  The CMS framework is quite flexible, well-developed, tested, and targeted for simulating compartmental models; this is evidenced by the recent adoption by Prof. Gerardin’s group at Northwestern for COVID. However, the monolithic nature of the program hinders bespoke model development such as Proctor’s recent genetic modeling for Polio and Lee’s mesoscale modeling.  A python-based tool that had similar functionality to the CMS framework, but more granular control over the model building, dynamic simulation, and event queue, would be a powerful modeling framework for both internal and external use.  The usability and adoption would potentially be higher as well.  This could be accomplished by hooking into the existing CMS infrastructure and using python’s .net packages.  In this case, we could leverage the model building and numerical algorithms, but have direct access to the simulator and event queue for modifications.  The project could also discover a different publicly available code-base to start from or leverage.

[original](https://github.com/InstituteforDiseaseModeling/pycms/files/4822533/ProjectPythonStochasticSims.docx)