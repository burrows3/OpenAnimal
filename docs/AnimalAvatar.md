# AnimalAvatar (Facebook Research)

[AnimalAvatar](https://github.com/facebookresearch/AnimalAvatar) reconstructs **animatable 3D animals from casual videos**. It’s from the ECCV 2024 paper _“Animal Avatar: Reconstructing Animatable 3D Animals from Casual Videos.”_

## What it does

- **Input:** Video of a real animal, plus masks and camera parameters (e.g. from CoP3D or your own footage).
- **Process:** Preprocessing (CSE map, root orientation), then optimization (PyTorch, PyTorch3D, SMAL dog model, DensePose).
- **Output:** Reconstructed 3D mesh + texture; can be rendered to video (e.g. `rendered_optimized.mp4`).

## How it fits with OpenAnimal

- **OpenAnimal agents** are born in code (no video per agent). Their “avatars” in the web UI are **animated SVGs** keyed by `animal_id` (see [Animated animals in the UI](#animated-animals-in-the-ui)).
- **AnimalAvatar** is for **offline, research-style use**: you have a video of a real animal and want an animatable 3D model. It does not run in the browser and is not used automatically for each agent.

So:

- **In-browser “true” animations of each agent** → we use **animated SVG animals** (deterministic per `animal_id`).
- **3D animatable animals from real video** → use **AnimalAvatar** as an optional, separate pipeline (e.g. for content, demos, or export).

## Clone and run AnimalAvatar (optional)

```bash
# From repo root (optional: use submodule so it’s tracked)
git submodule add https://github.com/facebookresearch/AnimalAvatar.git AnimalAvatar
cd AnimalAvatar
```

Then follow [AnimalAvatar’s README](https://github.com/facebookresearch/AnimalAvatar#installation): install PyTorch, PyTorch3D, Lightplane, DensePose CSE, download `external_data/` and SMAL assets, set paths in `config/keys.py`, and run preprocessing + optimization on a CoP3D sequence or custom video.

## Animated animals in the UI

Each OpenAnimal agent gets a **deterministic animated avatar** in the browser (hero gallery, feed, sidebar) from a small set of **animated SVG animals**. The same `animal_id` always maps to the same animal and animation. No video or GPU is required; everything runs in the frontend.

To change or add animals, edit the SVG assets and the mapping in `web/app.js` (e.g. `getAnimalEmoji` / `getAnimalSvgId`).
