# MDI TorchANI Tutorial
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/janash/mdi-ani-workshop)

You can complete this tutorial by [following the directions here](https://janash.github.io/setca-2024/driver_tutorial.html).
For easiest completion, open the starting repository using the Codespaces link above.

This is the starting repository for the tutorial on using the MolSSI Driver Interface to peform molecular dynamics simulations with TorchANI and LAMMPS.

To test this repository, first install `mdimechanic`

```bash
pip install mdimechanic
```

Run the following command to build the images:

```bash 
mdimechanic build
```

Then run the following command to run the starting code for the tutorial

```bash
mdimechanic run --name ani-tutorial
```
