<style>
#logo{text-align: center;}
#logo span {font-size: 46px;}
#logo img{
    display: inline;
    position: relative;
    top: 16px;
}
</style>

<div id="logo">
<img src="https://raw.githubusercontent.com/iLikeTrioxin/PetrolEngine/master/Engine/Resources/fuel_distributor128.png" height="64">
<span>Petrol engine</span>
</div>

<h4 align="center">Lead is a base repo to make your own petrol.</h4>

<div style="text-align: center;">
  <img src="https://img.shields.io/badge/C%2B%2B-17-brightgreen" alt="C++">
  <img src="https://img.shields.io/gitlab/license/iLikeTrioxin/Lead?color=blue" alt="License">
  <a href="https://yukiteru.xyz"><img src="https://img.shields.io/badge/My-Page-red" alt="Page"></a>
</div>

<div style="text-align: center;">
  <a href="#about">About</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#usage">Usage</a> •
  <a href="#credits">Credits</a>
</div>

<div style="text-align: center;">
<img src="https://cdn.discordapp.com/attachments/946029484014993418/1050479800734724147/2022_12_08_0wj_Kleki.png" alt="Example">
</div>

## About

Petrol Engine is a project that aims to be modular and fairly easy to use.
To achieve this it is split into several parts:
- Lead - a base repo to combine all the parts
- PetrolEngineCore - the core of the engine
- PetrolEngineOpenGL - most universal renderer API
- PetrolEngineOpenAl - a audio API

- PetrolEngineVulkan (WIP) - a renderer API that CAN speed up your app
- PetrolEngineMoltenVK (WIP) - a renderer API for macOS
- PetrolEngineEditor   (WIP) - a editor for the engine
- PetrolEngineKazan    (WIP) - a software renderer for embedded systems

## Requirements

To build Lead you need the following tools:
- [CMake](https://cmake.org/) - build system
- [Git](https://git-scm.com/) - version control system
- [Python](https://www.python.org/) - scripting language

## Usage

Clone the repo:
```
git clone --recursive https://github.com/iLikeTrioxin/Lead
```

Now you can add petrol addons.
To do so add a new line with the url of the github repo to the `addons` file.
```
# addons
https://github.com/iLikeTrioxin/PetrolEngineVulkan
```

If you use clion you can now open the project folder and it should everything for you.

Otherwise you can use cmake to generate the project files.
```
# create build folder
mkdir build
cd build

# generate project files
cmake ..
```
Now you should have project files for your IDE in the build folder.

## Credits

This software uses the following open source packages:

- [SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross)
- [openal-soft](https://github.com/kcat/openal-soft)
- [assimp](https://github.com/assimp/assimp)
- [freetype](https://github.com/freetype/freetype)
- [shaderc](https://github.com/google/shaderc)
- [glfw](https://github.com/glfw/glfw)
- [entt](https://github.com/skypjack/entt)
- [glm](https://github.com/g-truc/glm)
- [stb](https://github.com/nothings/stb)
