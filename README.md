## About

Petrol Engine is a project that aims to be modular and fairly easy to use.
To achieve this it is split into several parts:
- PetrolEngine - a base repo to combine all the parts
- PetrolEngineCore - the core of the engine
- PetrolEngineOpenGL - most universal renderer API
- PetrolEngineOpenAl - audio API
###### ... and more on the PetrolStation

## Requirements

To build Petrol you need the following tools:
- [CMake](https://cmake.org/) - build system
- [Git](https://git-scm.com/) - version control system
- [Python](https://www.python.org/) - scripting language

## Usage

Clone the repo:
```
git clone --recursive https://github.com/PetrolStation/PetrolEngine
```

Now you can add petrol addons.
To do so set CMake variable USE_ADDONS with the urls of the their github repos or their names if they are in PetrolStation.
```
set(USE_ADDONS Assimp Freetype OpenAL OpenGL GLFW ENet Bullet)
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
